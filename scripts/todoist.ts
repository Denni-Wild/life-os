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

interface Task {
  id: string;
  order: number;
  content: string;
  description: string;
  projectId?: string | null;
  sectionId?: string | null;
  isCompleted: boolean;
  labels: string[];
  priority: number;
  commentCount: number;
  createdAt: string;
  url: string;
  due?: {
    string: string;
    date: string;
    isRecurring: boolean;
    datetime?: string | null;
    timezone?: string | null;
  } | null;
}

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

function formatTask(task: Task) {
  const priority = "!".repeat(task.priority) || "-";
  const project = task.projectId ? `[${task.projectId}] ` : "";
  const labels = task.labels?.length ? ` @${task.labels.join(" @")}` : "";
  const description = task.description
    ? `\n   Description: ${task.description}`
    : "";
  const dueInfo = task.due
    ? ` (Due: ${task.due.date}${
        task.due.datetime
          ? ` at ${task.due.datetime.split("T")[1].slice(0, 5)}`
          : ""
      })`
    : "";
  const url = `\n   Link: ${task.url}`;

  return `[${priority}] ${project}${task.content}${labels}${dueInfo}${description}${url}`;
}

async function listTasks() {
  try {
    const tasks = await api.getTasks();
    const projects = await api.getProjects();
    const projectMap = new Map(projects.map((p) => [p.id, p.name]));

    console.log("\nAll Tasks:");
    console.log("----------");

    if (tasks.length === 0) {
      console.log("No tasks found");
    } else {
      // Group tasks by due date
      const tasksByDate = new Map<string, Task[]>();
      const noDateTasks: Task[] = [];

      tasks.forEach((task) => {
        if (task.due?.date) {
          const date = task.due.date;
          if (!tasksByDate.has(date)) {
            tasksByDate.set(date, []);
          }
          tasksByDate.get(date)!.push(task);
        } else {
          noDateTasks.push(task);
        }
      });

      // Sort dates
      const sortedDates = Array.from(tasksByDate.keys()).sort();

      // Print tasks by date
      sortedDates.forEach((date) => {
        const tasksForDate = tasksByDate.get(date)!;
        console.log(`\n${date}:`);
        console.log("-".repeat(date.length + 1));
        tasksForDate.forEach((task) => {
          const taskWithProjectName = {
            ...task,
            projectId: task.projectId
              ? projectMap.get(task.projectId) || task.projectId
              : undefined,
          };
          console.log(formatTask(taskWithProjectName));
          console.log(""); // Add empty line between tasks
        });
      });

      // Print tasks without due date
      if (noDateTasks.length > 0) {
        console.log("\nNo Due Date:");
        console.log("-----------");
        noDateTasks.forEach((task) => {
          const taskWithProjectName = {
            ...task,
            projectId: task.projectId
              ? projectMap.get(task.projectId) || task.projectId
              : undefined,
          };
          console.log(formatTask(taskWithProjectName));
          console.log(""); // Add empty line between tasks
        });
      }
    }
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
    const projects = await api.getProjects();
    const projectMap = new Map(projects.map((p) => [p.id, p.name]));
    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    console.log("\nUpcoming Tasks (Next 7 Days):");
    console.log("----------------------------");

    const upcomingTasks = tasks
      .filter((task) => {
        if (!task.due?.date) return false;
        const dueDate = new Date(task.due.date);
        return dueDate >= today && dueDate <= nextWeek;
      })
      .sort(
        (a, b) =>
          new Date(a.due!.date).getTime() - new Date(b.due!.date).getTime()
      );

    if (upcomingTasks.length === 0) {
      console.log("No upcoming tasks for the next 7 days");
    } else {
      upcomingTasks.forEach((task) => {
        const taskWithProjectName = {
          ...task,
          projectId: task.projectId
            ? projectMap.get(task.projectId) || task.projectId
            : undefined,
        };
        console.log(formatTask(taskWithProjectName));
        console.log(""); // Add empty line between tasks
      });
    }
  } catch (error) {
    console.error("Error fetching upcoming tasks:", error);
  }
}

async function listOverdue() {
  try {
    const tasks = await api.getTasks();
    const projects = await api.getProjects();
    const projectMap = new Map(projects.map((p) => [p.id, p.name]));
    const today = new Date();

    console.log("\nOverdue Tasks:");
    console.log("--------------");

    const overdueTasks = tasks.filter((task) => {
      if (!task.due?.date) return false;
      const dueDate = new Date(task.due.date);
      return dueDate < today;
    });

    if (overdueTasks.length === 0) {
      console.log("No overdue tasks");
    } else {
      overdueTasks.forEach((task) => {
        const taskWithProjectName = {
          ...task,
          projectId: task.projectId
            ? projectMap.get(task.projectId) || task.projectId
            : undefined,
        };
        console.log(formatTask(taskWithProjectName));
        console.log(""); // Add empty line between tasks
      });
    }
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
