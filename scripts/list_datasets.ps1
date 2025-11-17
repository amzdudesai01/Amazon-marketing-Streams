# List available Marketing Stream datasets
$accessToken = "Atza|gQCbSMz0AwEBAM9TvbNcKepTmKnFpSHprXD0FCN66VooqnXhvAUvs6u2AIS5As2JhAZ8W-IFBoeCb46T-Zf9OHGBvP67Oz8lhPOoWtPYUkHsNWljvJfjELNdnyUXkdm-iHdvpebAfjZktEUolE4XOmHt8rKFm9qiHLboHQnrAvMx-y8iZ6xLMznIf2KFMHXInVa-UQOkZs_iksFkp0brl1ydvF9JGhcPqOq9Cld07BgwIB14l_K7VtpquarjZgWRIW7RNu52Kt3IgEzhZw6uefj1ETuyCnD5RjNp8kPh4HV8rnT9kC3hmWSX2RObjUTTGXBFPnreJEbdtZnWq-9NcdQ6eV06z0WG7wygJ_x2zZsigO5GkWHVLQe5zb-d0-UapNh74TJaW1i7Pqk4Hpk-Bsfd_OfsZrXeUYQtFXX_RnAPlVxlgezdqJXr72DtQofHijRGZL-sJAQpHmVJtM8XSNcr96qneLw5AS3oHRnc1x_ojlQFNx5fsBeDosYqS7H3ypLWLDxXCyiU4rR4c3uHhH3j_mczC6g79rsYZSxkw69X7DjVd8uFTEdA5bRSIB6kZxk5qs9n3bu_ONS7GNWTtfx5gDFH_s0mhEC_qeDjSqUYfm2KQXgtMbcFHjm1SrDVYSFkgoi0d2r6eQ"
$clientId = "amzn1.application-oa2-client.f7c148c8a17344a5a878e3591b54e166"
$profileId = "2103765108426284"

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Amazon-Advertising-API-ClientId" = $clientId
    "Amazon-Advertising-API-Scope" = $profileId
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "https://advertising-api.amazon.com/streams/datasets" -Method Get -Headers $headers
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $_"
    Write-Host "Response: $($_.Exception.Response)"
}

