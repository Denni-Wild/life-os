import { TodoistApi, Task as TodoistTask } from "@doist/todoist-api-typescript";
import * as dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";
import { parse, stringify } from "yaml";

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
  to_delete?: boolean;
  deleted_at?: string;
  deleted_from?: string;
}

async function ensureDirectoryExists(filePath: string) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function parseYamlTasks(content: string): MemoryTask[] {
  try {
    const data = parse(content);
    if (!data || !data.tasks || !Array.isArray(data.tasks)) {
      return [];
    }
    return data.tasks;
  } catch (error) {
    console.error("Error parsing YAML:", error);
    return [];
  }
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
    const taskFiles = ["todoist.yml"];
    let updatedCount = 0;
    let deletedCount = 0;

    for (const file of taskFiles) {
      const filePath = path.join(baseDir, file);
      if (!fs.existsSync(filePath)) continue;

      const content = fs.readFileSync(filePath, "utf-8");
      const yamlContent = parse(content);
      const tasks: MemoryTask[] = yamlContent.tasks || [];
      let tasksModified = false;

      for (const task of tasks) {
        try {
          // Handle deletion first
          if (task.to_delete && task.todoist_id) {
            await api.deleteTask(task.todoist_id);
            task.deleted_at = new Date().toISOString();
            task.deleted_from = "memory";
            tasksModified = true;
            deletedCount++;
            console.log(`Deleted task: ${task.content}`);
            await sleep(500); // Rate limiting
            continue;
          }

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
            const newTask = await api.addTask(updateData);
            task.todoist_id = newTask.id; // Save the new task ID
            tasksModified = true;
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

      // Save updated tasks back to YAML if any new IDs were added or tasks were deleted
      if (tasksModified) {
        // Filter out deleted tasks
        yamlContent.tasks = tasks.filter(
          (task: MemoryTask) => !task.deleted_at
        );
        yamlContent.last_synced = new Date().toISOString();
        fs.writeFileSync(filePath, stringify(yamlContent));
        console.log(`✅ Updated task IDs saved to ${filePath}`);
      }
    }

    console.log(
      `✅ Updated ${updatedCount} tasks and deleted ${deletedCount} tasks in Todoist`
    );
  } catch (error: any) {
    console.error("Error exporting to Todoist:", error.message);
    if (error.httpStatusCode) {
      console.error(`HTTP Status Code: ${error.httpStatusCode}`);
    }
  }
}

async function importFromTodoist() {
  try {
    const tasks: TodoistTask[] = await api.getTasks();
    const projects = await api.getProjects();
    const projectMap = new Map(projects.map((p) => [p.id, p.name]));

    // Read existing YAML first
    const filePath = path.join("memory/tasks", "todoist.yml");
    let existingContent: { tasks: MemoryTask[] } = { tasks: [] };
    if (fs.existsSync(filePath)) {
      existingContent = parse(fs.readFileSync(filePath, "utf-8"));
    }

    // Create a set of current Todoist IDs
    const todoistIds = new Set(tasks.map((task) => task.id));

    // Check for deleted tasks
    existingContent.tasks = existingContent.tasks
      .map((task: MemoryTask) => {
        if (task.todoist_id && !todoistIds.has(task.todoist_id)) {
          // Task exists in YAML but not in Todoist - mark as deleted
          task.deleted_at = new Date().toISOString();
          task.deleted_from = "todoist";
        }
        return task;
      })
      .filter((task: MemoryTask) => !task.deleted_at); // Remove deleted tasks

    // Convert current Todoist tasks to memory format
    const memoryTasks: MemoryTask[] = tasks.map((task) => ({
      content: task.content,
      created_at: task.createdAt,
      todoist_id: task.id,
      priority: task.priority,
      project: task.projectId
        ? projectMap.get(task.projectId) || undefined
        : undefined,
      labels: task.labels,
      description: task.description || undefined,
      due_date: task.due?.date,
    }));

    // Write to memory file
    const content = {
      last_synced: new Date().toISOString(),
      tasks: memoryTasks,
    };

    fs.writeFileSync(filePath, stringify(content));
    console.log(`✅ Written ${memoryTasks.length} tasks to ${filePath}`);
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
