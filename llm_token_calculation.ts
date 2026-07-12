import { get_encoding } from "tiktok";

// 1. Setup Environment Configuration & Model Pricing
const API_KEY = process.env.OPENAI_API_KEY;
const MODEL = "gpt-4o-mini";

// Pricing per 1,000,000 tokens (Example for gpt-4o-mini)
const PRICE_PER_1M_INPUT_USD = 0.150;
const PRICE_PER_1M_OUTPUT_USD = 0.600;

// 2. Define the Conversations Array (The Wire Format)
const messages = [
  { role: "system", content: "You are a concise engineering assistant." },
  { role: "user", content: "Explain the architectural difference between prefill and decode phases in 2 sentences." }
];

// 3. Calculate Pre-flight Token Counts and Cost using tiktoken
function calculateInputCost(messagesArray) {
  // Use cl100k_base or o200k_base depending on model requirements
  const encoder = get_encoding("cl100k_base");
  let totalTokens = 0;

  // Each message has structural overhead tokens (<|im_start|>, roles, newlines)
  // Typically, OpenAI chat formats inject around 4 tokens per message + 3 tokens for the final assistant prompt priming
  for (const message of messagesArray) {
    totalTokens += 4; 
    totalTokens += encoder.encode(message.role).length;
    totalTokens += encoder.encode(message.content).length;
  }
  totalTokens += 3; // Prime the model to start generating the assistant response
  
  encoder.free(); // Free WASM memory leak safety
  
  const estimatedCost = (totalTokens / 1_000_000) * PRICE_PER_1M_INPUT_USD;
  return { totalTokens, estimatedCost };
}

async function executeRawStream() {
  const { totalTokens: inputTokens, estimatedCost: inputCost } = calculateInputCost(messages);
  console.log(`[Tokenomics] Pre-flight Analysis:`);
  console.log(`  Input Tokens: ${inputTokens}`);
  console.log(`  Estimated Input Cost: $${inputCost.toFixed(6)}\n`);

  // 4. Craft the Raw HTTP Wire Request Payload
  const payload = {
    model: MODEL,
    messages: messages,
    stream: true // Enforce Server-Sent Events (SSE)
  };

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${API_KEY}`
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error: ${response.status} - ${errorText}`);
  }

  // 5. Manual Parsing of the Server-Sent Events (SSE) Stream
  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  let outputTokensCounter = 0;
  
  process.stdout.write("[Assistant Stream]: ");

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    // Stream chunks can arrive as partial or split packets over TCP.
    // Append the decoded buffer chunk.
    buffer += decoder.decode(value, { stream: true });
    
    // SSE frames are separated by double newlines
    const lines = buffer.split("\n");
    
    // Hold onto the last incomplete line fragment
    buffer = lines.pop() || "";

    for (const line of lines) {
      const cleanedLine = line.trim();
      if (!cleanedLine) continue;
      if (!cleanedLine.startsWith("data: ")) continue;
      
      const rawData = cleanedLine.replace(/^data: /, "");
      
      // The stream officially terminates with "data: [DONE]"
      if (rawData === "[DONE]") {
        break;
      }

      try {
        const parsed = JSON.parse(rawData);
        const content = parsed.choices[0]?.delta?.content;
        
        if (content) {
          process.stdout.write(content);
          
          // Increment tracking tokens. In practice, calculating precise output tokens 
          // require a post-generation tiktoken run, as token sub-boundaries change.
          outputTokensCounter++; 
        }
      } catch (err) {
        // Handle malformed or partial JSON fragments safely
      }
    }
  }

  // 6. Final Financial Ledger Settlement
  console.log("\n\n[Tokenomics] Post-flight Analysis:");
  const outputCost = (outputTokensCounter / 1_000_000) * PRICE_PER_1M_OUTPUT_USD;
  const totalTransactionCost = inputCost + outputCost;
  
  console.log(`  Output Tokens (Estimated from chunks): ${outputTokensCounter}`);
  console.log(`  Output Cost: $${outputCost.toFixed(6)}`);
  console.log(`  Total Absolute Transaction Cost: $${totalTransactionCost.toFixed(6)}`);
}

executeRawStream().catch(console.error);