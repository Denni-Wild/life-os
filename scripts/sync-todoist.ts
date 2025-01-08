import { TodoistApi } from "@doist/todoist-api-typescript";
import * as dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";

dotenv.config();

if (!process.env.TODOIST_API_TOKEN) {
  console.error("Error: TODOIST_API_TOKEN is not set in .env file");
  process.exit(1);
}

const api = new TodoistApi(process.env.TODOIST_API_TOKEN);

interface MemoryTask {
  content: string;
  created_at: string;
  due_date?: string;
  priority?: number;
  project?: string;
  labels?: string[];
  description?: string;
  todoist_id?: string;
  completed_at?: string;
}

async function ensureDirectoryExists(filePath: string) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function formatTask(task: MemoryTask): string {
  const lines = [`## ${task.content}`, `- Created: ${task.created_at}`];

  if (task.due_date) lines.push(`- Due: ${task.due_date}`);
  if (task.priority) lines.push(`- Priority: ${task.priority}`);
  if (task.project) lines.push(`- Project: ${task.project}`);
  if (task.labels?.length) lines.push(`- Labels: ${task.labels.join(", ")}`);
  if (task.description) lines.push(`- Description: ${task.description}`);
  if (task.todoist_id) lines.push(`- Todoist ID: ${task.todoist_id}`);
  if (task.completed_at) lines.push(`- Completed: ${task.completed_at}`);

  return lines.join("\n") + "\n\n";
}

async function importFromTodoist() {
  try {
    const tasks = await api.getTasks();
    const projects = await api.getProjects();
    const projectMap = new Map(projects.map((p) => [p.id, p.name]));

    const memoryTasks: { [key: string]: MemoryTask[] } = {
      active: [],
      someday: [],
      waiting: [],
      completed: [],
    };

    tasks.forEach((task) => {
      const memoryTask: MemoryTask = {
        content: task.content,
        created_at: task.createdAt,
        todoist_id: task.id,
        priority: task.priority,
        project: task.projectId
          ? projectMap.get(task.projectId) || undefined
          : undefined,
        labels: task.labels,
        description: task.description || undefined,
      };

      if (task.due?.date) {
        memoryTask.due_date = task.due.date;
        memoryTasks.active.push(memoryTask);
      } else {
        memoryTasks.someday.push(memoryTask);
      }
    });

    // Write to memory files
    const baseDir = "memory/tasks";

    for (const [type, tasks] of Object.entries(memoryTasks)) {
      if (tasks.length > 0) {
        const filePath = path.join(baseDir, `${type}.md`);
        ensureDirectoryExists(filePath);

        const content = [
          `# ${type.charAt(0).toUpperCase() + type.slice(1)} Tasks`,
          `Last synced: ${new Date().toISOString()}`,
          "",
          ...tasks.map((task) => formatTask(task)),
        ].join("\n");

        fs.writeFileSync(filePath, content);
        console.log(`✅ Written ${tasks.length} tasks to ${filePath}`);
      }
    }
  } catch (error) {
    console.error("Error syncing with Todoist:", error);
  }
}

async function main() {
  const command = process.argv[2];

  switch (command) {
    case "import":
      await importFromTodoist();
      break;
    default:
      console.log("Usage: npm run todoist:sync import");
      break;
  }
}

main();
