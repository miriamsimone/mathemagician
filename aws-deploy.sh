#!/bin/bash

# Deploy Mathemagician to AWS ECS with Fargate

set -e

echo "🚀 Deploying Mathemagician to AWS ECS"
echo "====================================="
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Configuration
REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME="mathemagician-cluster"
SERVICE_NAME="mathemagician-service"
TASK_FAMILY="mathemagician-task"
ECR_REPO="mathemagician"
IMAGE_TAG=${IMAGE_TAG:-latest}

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account: $ACCOUNT_ID"
echo "🌍 Region: $REGION"
echo ""

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set. Set it with: export ANTHROPIC_API_KEY=your-api-key"
    echo ""
fi

# Create ECR repository if it doesn't exist
echo "📦 Ensuring ECR repository exists..."
aws ecr describe-repositories --repository-names $ECR_REPO --region $REGION 2>/dev/null || \
aws ecr create-repository \
    --repository-name $ECR_REPO \
    --region $REGION \
    --image-scanning-configuration scanOnPush=false

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"
IMAGE_URI="${ECR_URI}:${IMAGE_TAG}"

echo "🐳 ECR Repository: $ECR_URI"
echo ""

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

echo ""
echo "🏗️  Building Docker image (AMD64 platform for ECS Fargate)..."
docker build --platform linux/amd64 -t $ECR_REPO:$IMAGE_TAG .

echo ""
echo "🏷️  Tagging image for ECR..."
docker tag $ECR_REPO:$IMAGE_TAG $IMAGE_URI

echo ""
echo "⬆️  Pushing image to ECR..."
docker push $IMAGE_URI

echo ""
echo "✅ Image pushed successfully!"
echo ""

# Create ECS cluster if it doesn't exist
echo "🏗️  Ensuring ECS cluster exists..."
aws ecs describe-clusters --clusters $CLUSTER_NAME --region $REGION 2>/dev/null | grep -q "ACTIVE" || \
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION

# Create task execution role if it doesn't exist
EXECUTION_ROLE_NAME="ecsTaskExecutionRole"
echo "👤 Ensuring ECS task execution role exists..."

aws iam get-role --role-name $EXECUTION_ROLE_NAME 2>/dev/null || \
aws iam create-role \
    --role-name $EXECUTION_ROLE_NAME \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'

aws iam attach-role-policy \
    --role-name $EXECUTION_ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null || true

EXECUTION_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${EXECUTION_ROLE_NAME}"

# Register task definition
echo "📝 Registering ECS task definition..."

# Build environment variables JSON
ENV_VARS="["
ENV_VARS="${ENV_VARS}{\"name\":\"ENVIRONMENT\",\"value\":\"production\"},"
ENV_VARS="${ENV_VARS}{\"name\":\"REDIS_HOST\",\"value\":\"localhost\"},"
ENV_VARS="${ENV_VARS}{\"name\":\"REDIS_PORT\",\"value\":\"6379\"}"

if [ -n "$ANTHROPIC_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},{\"name\":\"ANTHROPIC_API_KEY\",\"value\":\"${ANTHROPIC_API_KEY}\"}"
fi

ENV_VARS="${ENV_VARS}]"

cat > task-definition.json <<EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "4096",
  "memory": "8192",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "mathemagician",
      "image": "$IMAGE_URI",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": $ENV_VARS,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mathemagician",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition \
    --cli-input-json file://task-definition.json \
    --region $REGION > /dev/null

rm task-definition.json

echo ""
echo "🌐 Setting up networking..."

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION)
echo "   VPC: $VPC_ID"

# Get subnets
SUBNETS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[*].SubnetId" --output text --region $REGION | tr '\t' ',')
echo "   Subnets: $SUBNETS"

# Create security group if it doesn't exist
SG_NAME="mathemagician-sg"
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text --region $REGION 2>/dev/null)

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    echo "   Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for Mathemagician ECS service" \
        --vpc-id $VPC_ID \
        --region $REGION \
        --query 'GroupId' \
        --output text)

    # Allow inbound on port 8000
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION
fi

echo "   Security Group: $SG_ID"
echo ""

# Check if service exists
SERVICE_EXISTS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION --query "services[0].status" --output text 2>/dev/null)

if [ "$SERVICE_EXISTS" = "ACTIVE" ]; then
    echo "🔄 Updating existing ECS service..."
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $TASK_FAMILY \
        --region $REGION \
        --force-new-deployment > /dev/null
else
    echo "🚀 Creating ECS service..."
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name $SERVICE_NAME \
        --task-definition $TASK_FAMILY \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" \
        --region $REGION > /dev/null
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "⏳ Waiting for task to start (this may take 1-2 minutes)..."

# Wait for service to stabilize
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION

# Get public IP
echo ""
echo "🔍 Finding public IP address..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $REGION --query "taskArns[0]" --output text)

if [ -n "$TASK_ARN" ] && [ "$TASK_ARN" != "None" ]; then
    ENI_ID=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --region $REGION --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text)
    PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region $REGION --query "NetworkInterfaces[0].Association.PublicIp" --output text)

    echo ""
    echo "🎉 Your API is live at: http://$PUBLIC_IP:8000"
    echo ""
    echo "Test endpoints:"
    echo "  Health: http://$PUBLIC_IP:8000/health"
    echo "  Docs:   http://$PUBLIC_IP:8000/docs"
    echo ""
    echo "To view logs:"
    echo "  aws logs tail /ecs/mathemagician --follow --region $REGION"
    echo ""
else
    echo "⚠️  Could not get public IP. Check ECS console for service status."
fi
