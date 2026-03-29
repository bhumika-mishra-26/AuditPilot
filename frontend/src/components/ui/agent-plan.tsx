"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  Circle,
  CircleAlert,
  CircleDotDashed,
  CircleX,
  Zap,
} from "lucide-react";
import { motion, AnimatePresence, LayoutGroup } from "motion/react";

// Type definitions
interface Subtask {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  tools?: string[]; // Optional array of MCP server tools
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  level: number;
  dependencies: string[];
  subtasks: Subtask[];
}

// Initial task data
const initialTasks: Task[] = [
  {
    id: "W1",
    title: "Vendor Onboarding Workflow",
    description: "Automated identity verification, KYC, and core ledger account creation.",
    status: "pending",
    priority: "high",
    level: 0,
    dependencies: [],
    subtasks: [
      {
        id: "W1.1",
        title: "Payload Validation",
        description: "Verify incoming request schema and data integrity.",
        status: "pending",
        priority: "high",
        tools: ["validate-node"],
      },
      {
        id: "W1.2",
        title: "Identity & Duplicate Check",
        description: "Cross-reference existing records to prevent duplicate account creation.",
        status: "pending",
        priority: "medium",
        tools: ["duplicate-detector"],
      },
      {
        id: "W1.3",
        title: "KYC/AML Verification",
        description: "Screen entities against global sanctions and watchlists.",
        status: "pending",
        priority: "high",
        tools: ["kyc-agent"],
      },
      {
        id: "W1.4",
        title: "Core Ledger Integration",
        description: "Initialize the financial record in the primary database.",
        status: "pending",
        priority: "high",
        tools: ["execution-orchestrator"],
      },
    ],
  },
  {
    id: "W2",
    title: "Procurement & Audit Cycle",
    description: "End-to-end management of vendor payments with real-time risk monitoring.",
    status: "pending",
    priority: "high",
    level: 0,
    dependencies: ["W1"],
    subtasks: [
      {
        id: "W2.1",
        title: "Document Ingestion",
        description: "Process invoices and purchase orders into the system.",
        status: "pending",
        priority: "high",
        tools: ["intake-bridge"],
      },
      {
        id: "W2.2",
        title: "Semantic Analysis",
        description: "Extract intent and line items from unstructured documentation.",
        status: "pending",
        priority: "high",
        tools: ["validation-engine"],
      },
      {
        id: "W2.3",
        title: "Risk Exposure Analysis",
        description: "Detect policy violations or fraudulent patterns.",
        status: "pending",
        priority: "high",
        tools: ["vendor-check-agent", "monitor-node"],
      },
      {
        id: "W2.4",
        title: "Approval & Disbursement",
        description: "Finalize financial release and log transaction proof.",
        status: "pending",
        priority: "medium",
        tools: ["approval-node", "payment-gateway"],
      },
    ],
  },
  {
    id: "W3",
    title: "AI Task Extraction Engine",
    description: "Distill actionable items and entity resolutions from audit logs.",
    status: "pending",
    priority: "medium",
    level: 1,
    dependencies: ["W1", "W2"],
    subtasks: [
      {
        id: "W3.1",
        title: "Feature Extraction",
        description: "Identify key events from the multi-agent execution trace.",
        status: "pending",
        priority: "medium",
        tools: ["extraction-llm"],
      },
      {
        id: "W3.2",
        title: "Ownership Resolution",
        description: "Assign identified tasks to respective business owners.",
        status: "pending",
        priority: "high",
        tools: ["owner-resolver-agent"],
      },
      {
        id: "W3.3",
        title: "Action Item Generation",
        description: "Write final results to the persistent audit trail.",
        status: "pending",
        priority: "high",
        tools: ["task-writer-core"],
      },
    ],
  },
];

export default function AgentPlan({ activeTaskId, overallStatus }: { activeTaskId?: string, overallStatus?: string }) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [expandedTasks, setExpandedTasks] = useState<string[]>([]);
  const [expandedSubtasks, setExpandedSubtasks] = useState<{
    [key: string]: boolean;
  }>({});

  React.useEffect(() => {
    if (activeTaskId) {
      setTasks(prev => prev.map(t => {
        if (t.id === activeTaskId) {
          // Map backend status to frontend display status
          const displayStatus = (overallStatus === 'completed') ? 'completed' : 
                                (overallStatus === 'failed') ? 'failed' : 'in-progress';
          return { ...t, status: displayStatus };
        }
        // W1 is completed if we are on W2 or W3
        if (t.id === "W1" && activeTaskId !== "W1") return { ...t, status: "completed" };
        // W2 is completed if we are on W3
        if (t.id === "W2" && activeTaskId === "W3") return { ...t, status: "completed" };
        
        return { ...t, status: "pending" };
      }));
      setExpandedTasks([activeTaskId]);
    } else {
      setTasks(initialTasks);
      setExpandedTasks([]);
    }
  }, [activeTaskId, overallStatus]);
  
  const prefersReducedMotion = 
    typeof window !== 'undefined' 
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches 
      : false;

  const toggleTaskExpansion = (taskId: string) => {
    setExpandedTasks((prev) =>
      prev.includes(taskId)
        ? prev.filter((id) => id !== taskId)
        : [...prev, taskId],
    );
  };

  const toggleSubtaskExpansion = (taskId: string, subtaskId: string) => {
    const key = `${taskId}-${subtaskId}`;
    setExpandedSubtasks((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const toggleTaskStatus = (taskId: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id === taskId) {
          const statuses = ["completed", "in-progress", "pending", "need-help", "failed"];
          const currentIndex = Math.floor(Math.random() * statuses.length);
          const newStatus = statuses[currentIndex];

          const updatedSubtasks = task.subtasks.map((subtask) => ({
            ...subtask,
            status: newStatus === "completed" ? "completed" : subtask.status,
          }));

          return {
            ...task,
            status: newStatus,
            subtasks: updatedSubtasks,
          };
        }
        return task;
      }),
    );
  };

  const toggleSubtaskStatus = (taskId: string, subtaskId: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id === taskId) {
          const updatedSubtasks = task.subtasks.map((subtask) => {
            if (subtask.id === subtaskId) {
              const newStatus =
                subtask.status === "completed" ? "pending" : "completed";
              return { ...subtask, status: newStatus };
            }
            return subtask;
          });

          const allSubtasksCompleted = updatedSubtasks.every(
            (s) => s.status === "completed",
          );

          return {
            ...task,
            subtasks: updatedSubtasks,
            status: allSubtasksCompleted ? "completed" : task.status,
          };
        }
        return task;
      }),
    );
  };

  const taskVariants = {
    hidden: { opacity: 0, y: prefersReducedMotion ? 0 : -5 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        type: prefersReducedMotion ? "tween" : "spring", 
        stiffness: 500, 
        damping: 30,
        duration: prefersReducedMotion ? 0.2 : undefined
      }
    },
    exit: { opacity: 0, y: prefersReducedMotion ? 0 : -5, transition: { duration: 0.15 } }
  };

  const subtaskListVariants = {
    hidden: { opacity: 0, height: 0, overflow: "hidden" },
    visible: { 
      height: "auto", 
      opacity: 1,
      overflow: "visible",
      transition: { 
        duration: 0.25, 
        staggerChildren: prefersReducedMotion ? 0 : 0.05,
        when: "beforeChildren",
        ease: [0.2, 0.65, 0.3, 0.9]
      }
    },
    exit: { height: 0, opacity: 0, overflow: "hidden", transition: { duration: 0.2, ease: [0.2, 0.65, 0.3, 0.9] } }
  };

  const subtaskVariants = {
    hidden: { opacity: 0, x: prefersReducedMotion ? 0 : -10 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { 
        type: prefersReducedMotion ? "tween" : "spring", 
        stiffness: 500, 
        damping: 25,
        duration: prefersReducedMotion ? 0.2 : undefined
      }
    },
    exit: { opacity: 0, x: prefersReducedMotion ? 0 : -10, transition: { duration: 0.15 } }
  };

  const subtaskDetailsVariants = {
    hidden: { opacity: 0, height: 0, overflow: "hidden" },
    visible: { opacity: 1, height: "auto", overflow: "visible", transition: { duration: 0.25, ease: [0.2, 0.65, 0.3, 0.9] } }
  };

  const statusBadgeVariants = {
    initial: { scale: 1 },
    animate: { 
      scale: prefersReducedMotion ? 1 : [1, 1.08, 1],
      transition: { duration: 0.35, ease: [0.34, 1.56, 0.64, 1] }
    }
  };

  return (
    <div className="text-white h-full overflow-auto w-full max-w-4xl mx-auto">
      <motion.div 
        className="bg-black/40 backdrop-blur-md rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
        initial={{ opacity: 0, y: 10 }}
        animate={{ 
          opacity: 1, 
          y: 0,
          transition: { duration: 0.3, ease: [0.2, 0.65, 0.3, 0.9] }
        }}
      >
        <LayoutGroup>
          <div className="p-4 overflow-hidden">
            <ul className="space-y-1 overflow-hidden">
              {tasks.map((task, index) => {
                const isExpanded = expandedTasks.includes(task.id);
                const isCompleted = task.status === "completed";

                return (
                  <motion.li
                    key={task.id}
                    className={` ${index !== 0 ? "mt-1 pt-2" : ""} `}
                    initial="hidden"
                    animate="visible"
                    variants={taskVariants}
                  >
                    <motion.div 
                      className="group flex items-center px-3 py-1.5 rounded-xl border border-transparent hover:border-white/5"
                      whileHover={{ 
                        backgroundColor: "rgba(255,255,255,0.03)",
                        transition: { duration: 0.2 }
                      }}
                    >
                      <motion.div
                        className="mr-3 flex-shrink-0 cursor-pointer"
                        onClick={(e) => { e.stopPropagation(); toggleTaskStatus(task.id); }}
                        whileTap={{ scale: 0.9 }}
                        whileHover={{ scale: 1.1 }}
                      >
                        <AnimatePresence mode="wait">
                          <motion.div
                            key={task.status}
                            initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                            animate={{ opacity: 1, scale: 1, rotate: 0 }}
                            exit={{ opacity: 0, scale: 0.8, rotate: 10 }}
                            transition={{ duration: 0.2, ease: [0.2, 0.65, 0.3, 0.9] }}
                          >
                            {task.status === "completed" ? (
                              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                            ) : task.status === "in-progress" ? (
                              <CircleDotDashed className="h-5 w-5 text-indigo-400" />
                            ) : task.status === "need-help" ? (
                              <CircleAlert className="h-5 w-5 text-amber-500" />
                            ) : task.status === "failed" ? (
                              <CircleX className="h-5 w-5 text-red-500" />
                            ) : (
                              <Circle className="text-gray-500 h-5 w-5" />
                            )}
                          </motion.div>
                        </AnimatePresence>
                      </motion.div>

                      <motion.div
                        className="flex min-w-0 flex-grow cursor-pointer items-center justify-between"
                        onClick={() => toggleTaskExpansion(task.id)}
                      >
                        <div className="mr-2 flex-1 truncate">
                          <span className={`text-sm font-semibold tracking-wide ${isCompleted ? "text-gray-500 line-through" : "text-white"}`}>
                            {task.title}
                          </span>
                        </div>

                        <div className="flex flex-shrink-0 items-center space-x-2 text-xs">
                          {/* Dependency badges removed to avoid user confusion between ID and dependency */}

                          <motion.span
                            className={`rounded-md px-2 py-0.5 font-bold uppercase tracking-wider text-[10px] ${
                              task.status === "completed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : task.status === "in-progress" ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                                  : task.status === "need-help" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                    : task.status === "failed" ? "bg-red-500/10 text-red-400 border border-red-500/20"
                                      : "bg-white/5 text-gray-400 border border-white/10"
                            }`}
                            variants={statusBadgeVariants}
                            initial="initial"
                            animate="animate"
                            key={task.status}
                          >
                            {task.status}
                          </motion.span>
                        </div>
                      </motion.div>
                    </motion.div>

                    <AnimatePresence mode="wait">
                      {isExpanded && task.subtasks.length > 0 && (
                        <motion.div 
                          className="relative overflow-hidden"
                          variants={subtaskListVariants}
                          initial="hidden"
                          animate="visible"
                          exit="hidden"
                          layout
                        >
                          <div className="absolute top-0 bottom-0 left-[22px] border-l border-dashed border-white/10" />
                          <ul className="mt-2 mr-2 mb-2 ml-4 space-y-1">
                            {task.subtasks.map((subtask) => {
                              const subtaskKey = `${task.id}-${subtask.id}`;
                              const isSubtaskExpanded = expandedSubtasks[subtaskKey];

                              return (
                                <motion.li
                                  key={subtask.id}
                                  className="group flex flex-col py-1 pl-6"
                                  onClick={() => toggleSubtaskExpansion(task.id, subtask.id)}
                                  variants={subtaskVariants}
                                  initial="hidden"
                                  animate="visible"
                                  exit="exit"
                                  layout
                                >
                                  <motion.div 
                                    className="flex flex-1 items-center rounded-lg p-1.5 border border-transparent hover:border-white/5"
                                    whileHover={{ backgroundColor: "rgba(255,255,255,0.03)", transition: { duration: 0.2 } }}
                                    layout
                                  >
                                    <motion.div
                                      className="mr-3 flex-shrink-0 cursor-pointer"
                                      onClick={(e) => { e.stopPropagation(); toggleSubtaskStatus(task.id, subtask.id); }}
                                      whileTap={{ scale: 0.9 }}
                                      whileHover={{ scale: 1.1 }}
                                      layout
                                    >
                                      <AnimatePresence mode="wait">
                                        <motion.div
                                          key={subtask.status}
                                          initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
                                          animate={{ opacity: 1, scale: 1, rotate: 0 }}
                                          exit={{ opacity: 0, scale: 0.8, rotate: 10 }}
                                          transition={{ duration: 0.2, ease: [0.2, 0.65, 0.3, 0.9] }}
                                        >
                                          {subtask.status === "completed" ? (
                                            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                                          ) : subtask.status === "in-progress" ? (
                                            <CircleDotDashed className="h-4 w-4 text-indigo-400" />
                                          ) : subtask.status === "need-help" ? (
                                            <CircleAlert className="h-4 w-4 text-amber-500" />
                                          ) : subtask.status === "failed" ? (
                                            <CircleX className="h-4 w-4 text-red-500" />
                                          ) : (
                                            <Circle className="text-gray-600 h-4 w-4" />
                                          )}
                                        </motion.div>
                                      </AnimatePresence>
                                    </motion.div>

                                    <span className={`cursor-pointer text-sm font-medium ${subtask.status === "completed" ? "text-gray-500 line-through" : "text-gray-300"}`}>
                                      {subtask.title}
                                    </span>
                                  </motion.div>

                                  <AnimatePresence mode="wait">
                                    {isSubtaskExpanded && (
                                      <motion.div 
                                        className="text-gray-400 mt-1 ml-2 border-l border-dashed border-white/10 pl-5 text-sm overflow-hidden"
                                        variants={subtaskDetailsVariants}
                                        initial="hidden"
                                        animate="visible"
                                        exit="hidden"
                                        layout
                                      >
                                        <p className="py-2 leading-relaxed">{subtask.description}</p>
                                        {subtask.tools && subtask.tools.length > 0 && (
                                          <div className="mt-1 mb-2 flex flex-wrap items-center gap-2">
                                            <span className="text-indigo-400 font-semibold text-xs uppercase tracking-widest">
                                              Agents Active:
                                            </span>
                                            <div className="flex flex-wrap gap-1.5">
                                              {subtask.tools.map((tool, idx) => (
                                                <motion.span
                                                  key={idx}
                                                  className="bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 rounded-md px-2 py-1 text-[10px] font-bold shadow-sm flex items-center gap-1"
                                                  initial={{ opacity: 0, y: -5 }}
                                                  animate={{ opacity: 1, y: 0, transition: { duration: 0.2, delay: idx * 0.05 } }}
                                                  whileHover={{ y: -1, backgroundColor: "rgba(99, 102, 241, 0.2)", transition: { duration: 0.2 } }}
                                                >
                                                  <Zap className="w-3 h-3 text-indigo-400" />
                                                  {tool}
                                                </motion.span>
                                              ))}
                                            </div>
                                          </div>
                                        )}
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </motion.li>
                              );
                            })}
                          </ul>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.li>
                );
              })}
            </ul>
          </div>
        </LayoutGroup>
      </motion.div>
    </div>
  );
}

// Ensure Zap icon is imported, let's add it manually since lucide-react has it
// Wait, Zap is not imported at the top. Let's make sure it is.
