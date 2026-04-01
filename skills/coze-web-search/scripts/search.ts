#!/usr/bin/env npx ts-node
import { SearchClient, Config, APIError } from "coze-coding-dev-sdk";

interface SearchOptions {
  query: string;
  type: "web" | "image";
  count: number;
  timeRange?: string;
  sites?: string;
  blockHosts?: string;
  needSummary: boolean;
  needContent: boolean;
  format: "json" | "text" | "markdown";
}

function formatWebResultsAsMarkdown(
  results: any[],
  summary?: string
): string {
  let md = "# Web Search Results\n\n";

  if (summary) {
    md += "## AI Summary\n\n";
    md += `${summary}\n\n`;
    md += "---\n\n";
  }

  md += "## Results\n\n";

  results.forEach((item, i) => {
    md += `### ${i + 1}. ${item.title}\n\n`;
    md += `- **URL**: ${item.url}\n`;
    md += `- **Source**: ${item.site_name || "Unknown"}\n`;
    if (item.publish_time) {
      md += `- **Published**: ${item.publish_time}\n`;
    }
    md += `\n${item.snippet}\n\n`;
    if (item.content) {
      md += `<details>\n<summary>Full Content</summary>\n\n${item.content.slice(0, 2000)}${item.content.length > 2000 ? "..." : ""}\n\n</details>\n\n`;
    }
  });

  return md;
}

function formatImageResultsAsMarkdown(results: any[]): string {
  let md = "# Image Search Results\n\n";

  results.forEach((item, i) => {
    md += `### ${i + 1}. ${item.title || "Untitled"}\n\n`;
    md += `- **Source**: ${item.site_name || "Unknown"}\n`;
    md += `- **Page URL**: ${item.url || "N/A"}\n`;
    md += `- **Image URL**: ${item.image?.url}\n`;
    if (item.image?.width && item.image?.height) {
      md += `- **Size**: ${item.image.width}x${item.image.height}\n`;
    }
    md += `\n![${item.title || "Image"}](${item.image?.url})\n\n`;
  });

  return md;
}

function formatWebResultsAsText(results: any[], summary?: string): string {
  let text = "";

  if (summary) {
    text += "=".repeat(60) + "\n";
    text += "AI SUMMARY\n";
    text += "=".repeat(60) + "\n";
    text += summary + "\n\n";
  }

  text += "=".repeat(60) + "\n";
  text += `SEARCH RESULTS (${results.length} items)\n`;
  text += "=".repeat(60) + "\n\n";

  results.forEach((item, i) => {
    text += `[${i + 1}] ${item.title}\n`;
    text += `    URL: ${item.url}\n`;
    text += `    Source: ${item.site_name || "Unknown"}\n`;
    if (item.publish_time) {
      text += `    Published: ${item.publish_time}\n`;
    }
    text += `    ${item.snippet.slice(0, 200)}${item.snippet.length > 200 ? "..." : ""}\n\n`;
  });

  return text;
}

function formatImageResultsAsText(results: any[]): string {
  let text = "=".repeat(60) + "\n";
  text += `IMAGE RESULTS (${results.length} items)\n`;
  text += "=".repeat(60) + "\n\n";

  results.forEach((item, i) => {
    text += `[${i + 1}] ${item.title || "Untitled"}\n`;
    text += `    Source: ${item.site_name || "Unknown"}\n`;
    text += `    Image: ${item.image?.url}\n`;
    if (item.image?.width && item.image?.height) {
      text += `    Size: ${item.image.width}x${item.image.height}\n`;
    }
    text += "\n";
  });

  return text;
}

async function main(): Promise<number> {
  const args = process.argv.slice(2);
  const options: SearchOptions = {
    query: "",
    type: "web",
    count: 10,
    needSummary: true,
    needContent: false,
    format: "text",
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if ((arg === "--query" || arg === "-q") && args[i + 1]) {
      options.query = args[++i];
    } else if (arg === "--type" && args[i + 1]) {
      options.type = args[++i] as "web" | "image";
    } else if (arg === "--count" && args[i + 1]) {
      options.count = parseInt(args[++i], 10);
    } else if (arg === "--time-range" && args[i + 1]) {
      options.timeRange = args[++i];
    } else if (arg === "--sites" && args[i + 1]) {
      options.sites = args[++i];
    } else if (arg === "--block-hosts" && args[i + 1]) {
      options.blockHosts = args[++i];
    } else if (arg === "--no-summary") {
      options.needSummary = false;
    } else if (arg === "--need-content") {
      options.needContent = true;
    } else if (arg === "--format" && args[i + 1]) {
      options.format = args[++i] as "json" | "text" | "markdown";
    } else if (arg === "--help") {
      console.log(`
Usage: npx ts-node search.ts [OPTIONS]

Options:
  -q, --query <text>      Search query (required)
  --type <type>           Search type: web or image (default: web)
  --count <n>             Number of results (default: 10)
  --time-range <range>    Time filter: 1d, 1w, 1m (web search only)
  --sites <domains>       Comma-separated domains to include
  --block-hosts <domains> Comma-separated domains to exclude
  --no-summary            Disable AI summary
  --need-content          Include full page content
  --format <fmt>          Output format: json, text, markdown (default: text)
  --help                  Show this help message

Examples:
  # Basic web search
  npx ts-node search.ts -q "Python programming"

  # Search with time filter and site restriction
  npx ts-node search.ts -q "AI news" --time-range 1w --sites "techcrunch.com,wired.com"

  # Image search
  npx ts-node search.ts -q "cute cats" --type image --count 20

  # Output as markdown
  npx ts-node search.ts -q "machine learning" --format markdown
`);
      return 0;
    }
  }

  if (!options.query) {
    console.error("Error: --query is required");
    return 1;
  }

  const config = new Config();
  const client = new SearchClient(config);

  try {
    let response: any;

    if (options.type === "image") {
      console.log(`Searching images for: "${options.query}"...`);
      response = await client.imageSearch(options.query, options.count);
    } else {
      const hasAdvancedOptions =
        options.timeRange || options.sites || options.blockHosts || options.needContent;

      if (hasAdvancedOptions) {
        console.log(`Advanced searching for: "${options.query}"...`);
        response = await client.advancedSearch(options.query, {
          searchType: "web",
          count: options.count,
          timeRange: options.timeRange,
          sites: options.sites,
          blockHosts: options.blockHosts,
          needSummary: options.needSummary,
          needContent: options.needContent,
        });
      } else {
        console.log(`Searching for: "${options.query}"...`);
        response = await client.webSearch(
          options.query,
          options.count,
          options.needSummary
        );
      }
    }

    let output: string;

    if (options.format === "json") {
      output = JSON.stringify(response, null, 2);
    } else if (options.format === "markdown") {
      if (options.type === "image") {
        output = formatImageResultsAsMarkdown(response.image_items || []);
      } else {
        output = formatWebResultsAsMarkdown(
          response.web_items || [],
          response.summary
        );
      }
    } else {
      if (options.type === "image") {
        output = formatImageResultsAsText(response.image_items || []);
      } else {
        output = formatWebResultsAsText(response.web_items || [], response.summary);
      }
    }

    console.log("\n" + output);

    const itemCount =
      options.type === "image"
        ? (response.image_items?.length || 0)
        : (response.web_items?.length || 0);
    console.log(`\nFound ${itemCount} results.`);

    return 0;
  } catch (error) {
    if (error instanceof APIError) {
      console.error(`API Error: ${error.message}`);
      console.error(`Status Code: ${error.statusCode}`);
    } else {
      console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
    return 1;
  }
}

main().then((code) => process.exit(code));
