aws_signing_helper credential-process ^
  --certificate ..\data\certificate.pem ^
  --private-key ..\data\privkey.pem ^
  --region sa-east-1 ^
  --trust-anchor-arn arn:aws:rolesanywhere:sa-east-1:101067722371:trust-anchor/c32fb318-8eae-4099-857b-37517cf5904e ^
  --profile-arn arn:aws:rolesanywhere:sa-east-1:101067722371:profile/c1b25145-d81a-4034-a27d-bdd293f836e0 ^
  --role-arn arn:aws:iam::101067722371:role/a1.sts_bedrock_test_role