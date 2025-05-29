Write-Host "Testing Chat Completions (streaming)..." -ForegroundColor Green
try {
    $body = @{
        model = "qwen2.5-coder:7b-instruct"
        messages = @(
            @{
                role = "user"
                content = "List 3 benefits of using Python"
            }
        )
        stream = $true
    } | ConvertTo-Json -Depth 10

    Write-Host "Request Body: $body" -ForegroundColor Cyan

    # For streaming, we need to use Invoke-WebRequest and handle the stream manually
    $response = Invoke-WebRequest -Uri "http://localhost:8000/v1/chat/completions" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "Response Status: $($response.StatusCode)" -ForegroundColor Green
    
    # Process the streaming content
    $content = $response.Content
    Write-Host "Received streaming content ($($content.Length) bytes)" -ForegroundColor Cyan
    
    # Parse and display stream chunks
    Write-Host "`nStreaming content preview:" -ForegroundColor Yellow
    
    # Display first 500 characters
    if ($content.Length -gt 500) {
        Write-Host $content.Substring(0, 500) -ForegroundColor Gray
        Write-Host "... (truncated)" -ForegroundColor Gray
    } else {
        Write-Host $content -ForegroundColor Gray
    }

} catch {
    Write-Host "Streaming request failed: $_" -ForegroundColor Red
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

Write-Host "`nStreaming test completed!" -ForegroundColor Green