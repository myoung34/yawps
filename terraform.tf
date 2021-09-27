resource "aws_iam_role" "yawps" {
  name               = "yawps"
  path               = "/lambda/"
  assume_role_policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "lambda.amazonaws.com"
        ]
      },
      "Effect": "Allow"
    }
  ]
}
POLICY

}

resource "aws_iam_role_policy" "yawps" {
  name = "yawps"
  role = aws_iam_role.yawps.name

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "organizations:ListTagsForResource"
            ],
            "Resource": [
              "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": [
              "arn:aws:kms:us-east-1:*:key/your-key-id"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:GetParameter"
            ],
            "Resource": [
              "arn:aws:ssm:us-east-1:*:parameter/ops/slack_token"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
              "arn:aws:logs:us-east-1:*:log-group:/aws/lambda/*",
              "arn:aws:logs:us-west-2:*:log-group:/aws/lambda/*"
            ]
        }
    ]
}
EOF

}

resource "aws_lambda_function" "yawps" {
  filename         = "yawps.zip"
  function_name    = var.function_name
  role             = aws_iam_role.yawps.arn
  handler          = "yawps.lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("yawps.zip")
  runtime          = "python3.6"
  timeout          = "30"
  environment {
    variables = {
      FOO = "0"
    }
  }

}

resource "aws_cloudwatch_event_rule" "securityhub_to_yawps" {
  name        = "securityhub_to_yawps"
  description = "Fire from SecurityHub events"

  event_pattern = <<PATTERN
{
  "source": [
    "aws.securityhub"
  ]
}
PATTERN
}

resource "aws_cloudwatch_event_target" "securityhub_to_yawps" {
  rule = aws_cloudwatch_event_rule.securityhub_to_yawps.name
  arn  = aws_lambda_function.yawps.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_yawps_for_securityhub" {
  statement_id  = "AllowExecutionFromCloudWatchToSecurityHubYawps"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.yawps.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.securityhub_to_yawps.arn
}
