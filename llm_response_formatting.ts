import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

// 1. Define the Strict Zod Schema
// We still use Zod as our single source of truth for validation and types.
const UserProfileSchema = z.object({
  fullName: z.string().describe("The user's first and last name"),
  age: z.number().int().describe("User age, must be a number"),
  hobbies: z.array(z.string()).describe("List of hobbies"),
  address: z.object({
    city: z.string(),
    zipCode: z.string().describe("5-digit US Zip code")
  })
});

// 2. Convert Zod to standard JSON Schema
// This prevents us from having to manually write a massive JSON Schema string.
const jsonSchemaDefinition = zodToJsonSchema(UserProfileSchema, "userProfile");

const API_KEY = process.env.OPENAI_API_KEY;

async function extractUserProfileStrict(userInput) {
  console.log("[Execution] Sending strict schema request to the API...");

  // Notice how minimal our system prompt is now. 
  // We don't need to beg the AI to use JSON or specify keys.
  const messages = [
    { role: "system", content: "Extract the user profile." },
    { role: "user", content: userInput }
  ];

  try {
    // 3. Execute the Raw HTTP Request using Structured Outputs
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: "gpt-4o-mini", // Requires a model that supports Structured Outputs
        messages: messages,
        temperature: 0.1,
        
        // 4. The Engineering Fix: Natively enforce the schema
        response_format: {
          type: "json_schema",
          json_schema: {
            name: "user_profile_extraction", // Give the schema a descriptive name
            schema: jsonSchemaDefinition.definitions.userProfile,
            strict: true // The model's logits are now constrained to this exact shape
          }
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const rawOutput = data.choices[0].message.content;
    
    // 5. Parse and Validate
    // Because strict: true is enabled, JSON.parse will not throw syntax errors
    const parsedJson = JSON.parse(rawOutput);
    
    // We pass it back through our Zod schema. 
    // In a TypeScript environment, this gives us our strict types back.
    // The risk of a Zod error here is effectively zero.
    const finalData = UserProfileSchema.parse(parsedJson);
    
    console.log("\n[Success] Data extracted and guaranteed to match schema:");
    return finalData;

  } catch (error) {
    console.error("\n[System Error]:", error.message);
  }
}

// Execute the streamlined pipeline
const messyInput = "Hey, I'm John Doe. I just turned 25. I love playing guitar and hiking. I live in Seattle, zipcode is 98105.";

extractUserProfileStrict(messyInput)
  .then(data => console.log(JSON.stringify(data, null, 2)));