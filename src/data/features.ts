import type { IconName } from "@/lib/icons";

export interface Feature {
  icon: IconName;
  title: string;
  body: string;
}

/** The core capability cards — angr's virtues, front and center. */
export const features: Feature[] = [
  {
    icon: "sigma",
    title: "Symbolic Execution",
    body: "A powerful concolic engine: explore every path at once, solve constraints, and reason about inputs that reach any state.",
  },
  {
    icon: "braces",
    title: "Decompilation",
    body: "Lift machine code to angr's AIL and recover readable pseudocode as C or Rust.",
  },
  {
    icon: "git-graph",
    title: "CFG Recovery",
    body: "Reconstruct control-flow graphs and call graphs with advanced static analyses, even on stripped and obfuscated targets.",
  },
  {
    icon: "binary",
    title: "Disassembly & Lifting",
    body: "Disassemble and lift to the VEX intermediate language, giving every architecture one uniform analysis surface.",
  },
  {
    icon: "cpu",
    title: "Multi-Architecture",
    body: "x86 / x86-64, ARM & AArch64, MIPS, PowerPC, and more — any host can analyze any guest.",
  },
  {
    icon: "puzzle",
    title: "Extensible by Design",
    body: "Hook anything, register custom analyses, SimProcedures, and exploration techniques. If you can script it in Python, angr can run it.",
  },
  {
    icon: "terminal",
    title: "Pythonic API",
    body: "A clean, scriptable Python interface. Drop into a REPL, wire angr into your tooling, or build something entirely new on top.",
  },
  {
    icon: "git-fork",
    title: "Free & Open Source",
    body: "Released under the permissive BSD license and developed in the open. Battle-tested in research, CTFs, and the DARPA CGC.",
  },
];
