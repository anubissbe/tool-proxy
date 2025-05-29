Write-Host "Testing Ollama Proxy Health..." -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "Health check response: $($health | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nTesting Chat Completions (non-streaming)..." -ForegroundColor Green
try {
    $body = @{
        model = "qwen2.5-coder:7b-instruct"
        messages = @(
            @{
                role = "user"
                content = "Write a simple hello world function in Python"
            }
        )
        stream = $false
    } | ConvertTo-Json -Depth 10

    Write-Host "Request Body: $body" -ForegroundColor Cyan

    $response = Invoke-RestMethod -Uri "http://localhost:8000/v1/chat/completions" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    Write-Host "Response: $($response | ConvertTo-Json -Depth 10)" -ForegroundColor Green
    
    # Check for crucial OpenAI compatibility properties
    if (-not $response.choices -or $response.choices.Count -eq 0) {
        Write-Host "Error: No choices in response" -ForegroundColor Red
        exit 1
    }
    
    if (-not $response.choices[0].message) {
        Write-Host "Error: No message in response choices" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Content from response: $($response.choices[0].message.content)" -ForegroundColor Yellow

} catch {
    Write-Host "Chat completions request failed: $_" -ForegroundColor Red
    Write-Host "Exception details: $($_.Exception)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host "`nAll tests passed successfully!" -ForegroundColor Green