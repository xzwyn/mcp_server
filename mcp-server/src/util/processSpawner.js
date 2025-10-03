import { spawn } from "node:child_process";

export async function spawnCli(pythonCliPath, cliArgs) {
  const pythonExe = process.env.PYTHON_EXE || "python";
  const args = [pythonCliPath, ...cliArgs];

  const child = spawn(pythonExe, args, { stdio: ["ignore", "pipe", "pipe"] });

  let stdout = "";
  let stderr = "";

  child.stdout.on("data", (d) => (stdout += d.toString()));
  child.stderr.on("data", (d) => (stderr += d.toString()));

  const exitCode = await new Promise((resolve) => child.on("close", resolve));

  if (exitCode !== 0) {
    return {
      isError: true,
      content: [{ type: "text", text: stderr || stdout || `Exited with code ${exitCode}` }]
    };
  }

  return {
    isError: false,
    content: [{ type: "text", text: stdout.trim() }]
  };
}
