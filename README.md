# ECR-credential-provider

After k8s-version `v1.27` the kubelet will no longer try to authenticate with ECR automatically for private registries on AWS. Instead, the extensible kubelet mechanism for image credential providers should be used.
Unfortunately, the ECR credential-provider is not pushed by [cloud-provider-aws](https://github.com/kubernetes/cloud-provider-aws) in any image. To work around this we use this repository to build an image so that it can be used by the gardener-node-agent.
