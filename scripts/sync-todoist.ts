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

function parseMarkdownTasks(content: string): MemoryTask[] {
  const tasks: MemoryTask[] = [];
  const sections = content.split("##").slice(1); // Skip the header

  for (const section of sections) {
    const lines = section.trim().split("\n");
    const task: Partial<MemoryTask> = {
      content: lines[0].trim(),
    };

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line.startsWith("- ")) continue;

      const [key, ...valueParts] = line.slice(2).split(": ");
      const value = valueParts.join(": ").trim();

      switch (key.toLowerCase()) {
        case "created":
          task.created_at = value;
          break;
        case "due":
          task.due_date = value;
          break;
        case "priority":
          task.priority = parseInt(value);
          break;
        case "project":
          task.project = value;
          break;
        case "labels":
          task.labels = value.split(",").map((l) => l.trim());
          break;
        case "description":
          task.description = value;
          break;
        case "todoist id":
          task.todoist_id = value;
          break;
        case "completed":
          task.completed_at = value;
          break;
      }
    }

    if (task.content && task.created_at) {
      tasks.push(task as MemoryTask);
    }
  }

  return tasks;
}

async function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function exportToTodoist() {
  try {
    // First get all projects to create a map and ensure they exist
    const projects = await api.getProjects();
    const projectMap = new Map<string, string>();

    for (const project of projects) {
      projectMap.set(project.name, project.id);
    }

    // Read tasks from memory files
    const baseDir = "memory/tasks";
    const taskFiles = ["active.md", "someday.md"];
    let updatedCount = 0;

    for (const file of taskFiles) {
      const filePath = path.join(baseDir, file);
      if (!fs.existsSync(filePath)) continue;

      const content = fs.readFileSync(filePath, "utf-8");
      const tasks = parseMarkdownTasks(content);

      for (const task of tasks) {
        try {
          const updateData: any = {
            content: task.content,
            priority: task.priority || 1,
          };

          // Handle project
          if (task.project) {
            let projectId = projectMap.get(task.project);
            if (!projectId) {
              // Create project if it doesn't exist
              const newProject = await api.addProject({ name: task.project });
              await sleep(500); // Rate limiting
              projectId = newProject.id;
              projectMap.set(task.project, projectId);
            }
            updateData.projectId = projectId;
          }

          // Handle due date
          if (task.due_date) {
            updateData.dueDate = task.due_date;
          }

          // Handle labels
          if (task.labels) {
            updateData.labels = task.labels;
          }

          // Handle description
          if (task.description) {
            updateData.description = task.description;
          }

          if (task.todoist_id) {
            // Update existing task
            await api.updateTask(task.todoist_id, updateData);
            console.log(`Updated task: ${task.content}`);
          } else {
            // Create new task
            await api.addTask(updateData);
            console.log(`Created task: ${task.content}`);
          }

          await sleep(500); // Rate limiting between operations
          updatedCount++;
        } catch (taskError: any) {
          console.error(
            `Error processing task "${task.content}":`,
            taskError.message
          );
          if (taskError.httpStatusCode === 503) {
            console.log(
              "Service temporarily unavailable. Waiting 5 seconds..."
            );
            await sleep(5000);
          }
          continue;
        }
      }
    }

    console.log(`✅ Updated ${updatedCount} tasks in Todoist`);
  } catch (error: any) {
    console.error("Error exporting to Todoist:", error.message);
    if (error.httpStatusCode) {
      console.error(`HTTP Status Code: ${error.httpStatusCode}`);
    }
  }
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
    case "export":
      await exportToTodoist();
      break;
    default:
      console.log("Usage: npm run todoist:sync [import|export]");
      break;
  }
}

main();
