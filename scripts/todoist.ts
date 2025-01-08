import { TodoistApi } from "@doist/todoist-api-typescript";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

if (!process.env.TODOIST_API_TOKEN) {
  console.error("Error: TODOIST_API_TOKEN is not set in .env file");
  process.exit(1);
}

// Initialize the Todoist client
const api = new TodoistApi(process.env.TODOIST_API_TOKEN);

async function addTask(content: string, dueDate?: string, priority?: number) {
  try {
    const task = await api.addTask({
      content,
      dueString: dueDate,
      priority: priority || 1,
    });
    console.log(`✅ Task added: ${task.content}`);
    return task;
  } catch (error) {
    console.error("Error adding task:", error);
    return null;
  }
}

async function listTasks() {
  try {
    const tasks = await api.getTasks();
    const today = new Date().toISOString().split("T")[0];

    console.log("\nToday's Tasks:");
    console.log("--------------");

    tasks
      .filter((task) => task.due?.date === today)
      .forEach((task) => {
        const priority = "!".repeat(task.priority) || "-";
        console.log(
          `[${priority}] ${task.content}${
            task.due ? ` (Due: ${task.due.date})` : ""
          }`
        );
      });
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
}

async function listProjects() {
  try {
    const projects = await api.getProjects();
    console.log("\nProjects:");
    console.log("---------");
    projects.forEach((project) => {
      console.log(`[${project.id}] ${project.name}`);
    });
  } catch (error) {
    console.error("Error fetching projects:", error);
  }
}

async function manageContexts() {
  try {
    const labels = await api.getLabels();
    console.log("\nContext Labels:");
    console.log("--------------");
    labels.forEach((label) => {
      console.log(`@${label.name}`);
    });
  } catch (error) {
    console.error("Error fetching labels:", error);
  }
}

async function completeTask(taskId: string) {
  try {
    await api.closeTask(taskId);
    console.log(`✅ Task ${taskId} completed`);
  } catch (error) {
    console.error("Error completing task:", error);
  }
}

async function listUpcoming() {
  try {
    const tasks = await api.getTasks();
    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    console.log("\nUpcoming Tasks (Next 7 Days):");
    console.log("----------------------------");

    tasks
      .filter((task) => {
        if (!task.due?.date) return false;
        const dueDate = new Date(task.due.date);
        return dueDate >= today && dueDate <= nextWeek;
      })
      .sort(
        (a, b) =>
          new Date(a.due!.date).getTime() - new Date(b.due!.date).getTime()
      )
      .forEach((task) => {
        const priority = "!".repeat(task.priority) || "-";
        console.log(`[${priority}] ${task.content} (Due: ${task.due!.date})`);
      });
  } catch (error) {
    console.error("Error fetching upcoming tasks:", error);
  }
}

async function listOverdue() {
  try {
    const tasks = await api.getTasks();
    const today = new Date();

    console.log("\nOverdue Tasks:");
    console.log("--------------");

    tasks
      .filter((task) => {
        if (!task.due?.date) return false;
        const dueDate = new Date(task.due.date);
        return dueDate < today;
      })
      .forEach((task) => {
        const priority = "!".repeat(task.priority) || "-";
        console.log(`[${priority}] ${task.content} (Due: ${task.due!.date})`);
      });
  } catch (error) {
    console.error("Error fetching overdue tasks:", error);
  }
}

// Handle command line arguments
const command = process.argv[2];
const args = process.argv.slice(3);

async function main() {
  switch (command) {
    case "add":
      if (args.length === 0) {
        console.error(
          'Usage: npm run todos:add "Task content" [due_date] [priority]'
        );
        process.exit(1);
      }
      const [content, dueDate, priority] = args;
      await addTask(
        content,
        dueDate,
        priority ? parseInt(priority) : undefined
      );
      break;

    case "projects":
      await listProjects();
      break;

    case "contexts":
      await manageContexts();
      break;

    case "complete":
      if (args.length === 0) {
        console.error("Usage: npm run todos:complete <task_id>");
        process.exit(1);
      }
      await completeTask(args[0]);
      break;

    case "upcoming":
      await listUpcoming();
      break;

    case "overdue":
      await listOverdue();
      break;

    case "list":
    default:
      await listTasks();
      break;
  }
}

main();
