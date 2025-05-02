"""
Graphical User Interface for Belief Revision Agent.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import traceback
import sys
import os

# Add the current directory and parent directory to the path
sys.path.append('.')
sys.path.append('..')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try importing the modules
try:
    from propositional_logic import Atom, Not, And, Or, Implies, Equivalent, parse_formula
    from belief_base import BeliefBase
    from entailment import ResolutionChecker
    from contraction import PartialMeetContraction
    from expansion import Expansion, Revision
    print("Successfully imported belief revision modules")
except ImportError as e:
    print(f"Import error: {e}")
    print("Current path:", os.getcwd())
    print("Python path:", sys.path)
    messagebox.showerror("Import Error", f"Failed to import belief revision modules: {e}\n\nCheck console for more details.")
    raise


class BeliefRevisionGUI:
    """GUI for the Belief Revision Agent."""

    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Belief Revision Agent")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)

        # Initialize the belief revision components
        self.belief_base = BeliefBase()
        self.entailment_checker = ResolutionChecker()
        self.contraction = PartialMeetContraction(self.entailment_checker)
        self.expansion = Expansion(self.entailment_checker)
        self.revision = Revision(self.entailment_checker)

        # Create a nice theme
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            try:
                style.theme_use('default')
            except tk.TclError:
                pass  # If no theme is available, just use the system default

        # Configure background colors
        bg_color = "#f5f5f5"  # Light gray background
        frame_bg = "#e0e0e0"  # Slightly darker for frames

        self.root.configure(bg=bg_color)

        # Create the main frames
        self.create_frames(frame_bg)

        # Create the formula entry section
        self.create_formula_entry()

        # Create the belief base display
        self.create_belief_base_display()

        # Create the operations section
        self.create_operations_section()

        # Create the results section
        self.create_results_section()

        # Create the bottom buttons
        self.create_bottom_buttons()

        # Create help section
        self.create_help_section()

        # Refresh the belief base display
        self.refresh_belief_base()

        # Log initial message
        self.log_result("System initialized. Please add belief formulas.")

        # Bind debug key
        self.root.bind("<F12>", self.debug_info)

    def debug_info(self, event=None):
        """Display debug information."""
        info = f"Python version: {sys.version}\n"
        info += f"Working directory: {os.getcwd()}\n"
        info += f"Python path: {sys.path}\n"
        info += f"BeliefBase formulas: {self.belief_base.get_all_formulas()}\n"

        messagebox.showinfo("Debug Information", info)

    def create_frames(self, frame_bg):
        """Create the main frames for the GUI."""
        # Top frame for formula entry
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Left frame for belief base display
        self.left_frame = ttk.Frame(self.root, padding="10")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Right frame for operations
        self.right_frame = ttk.Frame(self.root, padding="10")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=5)

        # Center frame for results
        self.center_frame = ttk.Frame(self.root, padding="10")
        self.center_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Bottom frame for buttons
        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def create_formula_entry(self):
        """Create the formula entry section."""
        formula_frame = ttk.LabelFrame(self.top_frame, text="Add Formula", padding="10")
        formula_frame.pack(fill=tk.X, padx=5, pady=5)

        # Formula entry
        ttk.Label(formula_frame, text="Formula:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.formula_entry = ttk.Entry(formula_frame, width=40)
        self.formula_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Priority entry
        ttk.Label(formula_frame, text="Priority:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.priority_var = tk.StringVar(value="1")
        priority_entry = ttk.Spinbox(formula_frame, from_=1, to=10, textvariable=self.priority_var, width=5)
        priority_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Add button
        add_button = ttk.Button(formula_frame, text="Add to Belief Base", command=self.add_formula)
        add_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        # Syntax help
        syntax_label = ttk.Label(
            formula_frame,
            text="Syntax: p, q (atoms), ~p (negation), p & q (AND), p | q (OR), p -> q (implies), p <-> q (equivalent)"
        )
        syntax_label.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky=tk.W)

    def create_belief_base_display(self):
        """Create the belief base display section."""
        belief_base_frame = ttk.LabelFrame(self.left_frame, text="Current Belief Base", padding="10")
        belief_base_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrolled text widget to display the belief base
        self.belief_base_text = scrolledtext.ScrolledText(
            belief_base_frame, wrap=tk.WORD, width=40, height=15
        )
        self.belief_base_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.belief_base_text.config(state=tk.DISABLED)

        # Clear button
        clear_button = ttk.Button(belief_base_frame, text="Clear Belief Base", command=self.clear_belief_base)
        clear_button.pack(padx=5, pady=5)

    def create_operations_section(self):
        """Create the operations section."""
        operations_frame = ttk.LabelFrame(self.right_frame, text="Operations", padding="10")
        operations_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Operation type selection
        ttk.Label(operations_frame, text="Operation:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.operation_var = tk.StringVar(value="Contraction")
        operation_combo = ttk.Combobox(
            operations_frame,
            textvariable=self.operation_var,
            values=["Contraction", "Expansion", "Revision"]
        )
        operation_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        operation_combo.state(['readonly'])

        # Formula entry for operation
        ttk.Label(operations_frame, text="Formula:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.operation_formula_entry = ttk.Entry(operations_frame, width=30)
        self.operation_formula_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        # Priority for expansion/revision
        ttk.Label(operations_frame, text="Priority:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.operation_priority_var = tk.StringVar(value="1")
        operation_priority_entry = ttk.Spinbox(
            operations_frame, from_=1, to=10,
            textvariable=self.operation_priority_var, width=5
        )
        operation_priority_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Execute button with command binding
        execute_button = ttk.Button(operations_frame, text="Execute", command=self.execute_operation)
        execute_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        # Check entailment section
        entailment_frame = ttk.LabelFrame(operations_frame, text="Check Entailment", padding="10")
        entailment_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=15, sticky=tk.W+tk.E)

        ttk.Label(entailment_frame, text="Formula:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.entailment_formula_entry = ttk.Entry(entailment_frame, width=30)
        self.entailment_formula_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)

        # Check button with command binding and double-check it's working
        check_button = ttk.Button(entailment_frame, text="Check", command=self.check_entailment)
        check_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

    def create_results_section(self):
        """Create the results section."""
        results_frame = ttk.LabelFrame(self.center_frame, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrolled text widget to display results
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_text.config(state=tk.DISABLED)

    def create_bottom_buttons(self):
        """Create the bottom buttons."""
        button_frame = ttk.Frame(self.bottom_frame, padding="10")
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # Help button
        help_button = ttk.Button(button_frame, text="Help", command=self.show_help)
        help_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Example button
        example_button = ttk.Button(button_frame, text="Load Example", command=self.load_example)
        example_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Clear results button
        clear_results_button = ttk.Button(button_frame, text="Clear Results", command=self.clear_results)
        clear_results_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def create_help_section(self):
        """Create the help section."""
        self.help_text = """
Belief Revision Agent Help:

Formula Syntax:
- Atoms: p, q, r, ...
- Negation: ~p (NOT p)
- Conjunction: p & q (p AND q)
- Disjunction: p | q (p OR q)
- Implication: p -> q (p IMPLIES q)
- Equivalence: p <-> q (p is EQUIVALENT to q)

Operations:
- Contraction: Removes a belief from the belief base
- Expansion: Adds a belief to the belief base
- Revision: Updates the belief base with a new belief while maintaining consistency

Examples:
- p & q
- p -> q
- ~(p | q)
- (p -> q) & (q -> r)
        """

    def show_help(self):
        """Show the help dialog."""
        messagebox.showinfo("Help", self.help_text)

    def load_example(self):
        """Load an example belief base."""
        if self.belief_base.get_all_formulas() and not messagebox.askyesno("Confirm", "This will replace your current belief base. Continue?"):
            return

        # Clear current belief base
        self.belief_base = BeliefBase()

        # Add example formulas
        p = Atom('p')  # "It is raining"
        q = Atom('q')  # "The ground is wet"
        r = Atom('r')  # "The floor is slippery"

        # "If it rains, the ground is wet" (priority 3)
        self.belief_base.add(Implies(p, q), 3)

        # "It is raining" (priority 2)
        self.belief_base.add(p, 2)

        # "If the ground is wet, the floor is slippery" (priority 2)
        self.belief_base.add(Implies(q, r), 2)

        # Refresh the display and log the action
        self.refresh_belief_base()
        self.log_result("Example belief base loaded:\n- p: It is raining\n- q: The ground is wet\n- r: The floor is slippery\n- p -> q: If it rains, the ground becomes wet\n- q -> r: If the ground is wet, the floor becomes slippery")

    def add_formula(self):
        """Add a formula to the belief base."""
        formula_str = self.formula_entry.get().strip()
        if not formula_str:
            messagebox.showerror("Error", "Please enter a formula.")
            return

        try:
            priority = int(self.priority_var.get())
            if priority < 1:
                messagebox.showerror("Error", "Priority must be at least 1.")
                return

            print(f"Parsing formula: '{formula_str}'")
            formula = parse_formula(formula_str)
            print(f"Parsed formula: {formula}")

            self.belief_base.add(formula, priority)

            self.log_result(f"Added formula '{formula}' to belief base (priority: {priority}).")
            self.refresh_belief_base()
            self.formula_entry.delete(0, tk.END)

        except Exception as e:
            print(f"Error parsing formula: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Error adding formula: {str(e)}")
            self.log_result(f"Error: Failed to add formula - {str(e)}")

    def clear_belief_base(self):
        """Clear the belief base."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the belief base?"):
            self.belief_base = BeliefBase()
            self.refresh_belief_base()
            self.log_result("Belief base cleared.")

    def refresh_belief_base(self):
        """Refresh the belief base display."""
        self.belief_base_text.config(state=tk.NORMAL)
        self.belief_base_text.delete(1.0, tk.END)

        beliefs = self.belief_base.get_all_formulas()
        if not beliefs:
            self.belief_base_text.insert(tk.END, "Empty belief base")
        else:
            sorted_beliefs = sorted([(f, self.belief_base.get_priority(f)) for f in beliefs],
                                     key=lambda x: x[1], reverse=True)

            for formula, priority in sorted_beliefs:
                self.belief_base_text.insert(tk.END, f"{formula} (priority: {priority})\n")

        self.belief_base_text.config(state=tk.DISABLED)

    def execute_operation(self):
        """Execute the selected operation."""
        print("Execute operation button clicked")
        operation = self.operation_var.get()
        formula_str = self.operation_formula_entry.get().strip()

        if not formula_str:
            messagebox.showerror("Error", "Please enter a formula for the operation.")
            return

        try:
            print(f"Parsing operation formula: '{formula_str}'")
            formula = parse_formula(formula_str)
            print(f"Parsed operation formula: {formula}")

            if operation == "Contraction":
                self.log_result(f"Performing contraction: '{formula}'...")
                result = self.contraction.contract(self.belief_base, formula)
                self.log_result(f"Contraction complete: Formula '{formula}' removed from belief base.")

            elif operation == "Expansion":
                priority = int(self.operation_priority_var.get())
                self.log_result(f"Performing expansion: Adding formula '{formula}' (priority: {priority})...")
                result = self.expansion.expand(self.belief_base, formula, priority)
                self.log_result(f"Expansion complete: Formula '{formula}' added to belief base.")

            elif operation == "Revision":
                priority = int(self.operation_priority_var.get())
                self.log_result(f"Performing revision: Revising with formula '{formula}' (priority: {priority})...")
                result = self.revision.revise(self.belief_base, formula, priority)
                self.log_result(f"Revision complete: Belief base updated with formula '{formula}'.")

            # Update the belief base
            self.belief_base = result
            self.refresh_belief_base()
            self.operation_formula_entry.delete(0, tk.END)

        except Exception as e:
            print(f"Error in execute_operation: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Error executing operation: {str(e)}")
            self.log_result(f"Error: Failed to execute operation - {str(e)}")

    def check_entailment(self):
        """Check if a formula is entailed by the belief base."""
        print("Check entailment button clicked")
        formula_str = self.entailment_formula_entry.get().strip()

        if not formula_str:
            messagebox.showerror("Error", "Please enter a formula to check entailment.")
            return

        try:
            print(f"Parsing entailment formula: '{formula_str}'")
            formula = parse_formula(formula_str)
            print(f"Parsed entailment formula: {formula}")

            print("Getting belief base conjunction...")
            belief_conjunction = self.belief_base._get_conjunction()
            print(f"Belief conjunction: {belief_conjunction}")

            self.log_result(f"Checking if belief base entails '{formula}'...")
            print(f"Checking entailment of {formula}...")

            result = self.entailment_checker.entails(belief_conjunction, formula)
            print(f"Entailment result: {result}")

            if result:
                self.log_result(f"Result: Belief base entails '{formula}'.")
            else:
                self.log_result(f"Result: Belief base does NOT entail '{formula}'.")

            # Add an explicit messagebox for more visibility
            messagebox.showinfo("Entailment Result",
                                 f"The belief base {'does' if result else 'does NOT'} entail '{formula}'.")

        except Exception as e:
            print(f"Error in check_entailment: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Error", f"Error checking entailment: {str(e)}")
            self.log_result(f"Error: Failed to check entailment - {str(e)}")

    def log_result(self, message):
        """Log a result to the results text box."""
        print(f"Logging: {message}")
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def clear_results(self):
        """Clear the results text box."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)


def main():
    """Main function to start the GUI."""
    root = tk.Tk()
    try:
        app = BeliefRevisionGUI(root)
        print("GUI initialized successfully")
        root.mainloop()
    except Exception as e:
        print(f"Error initializing GUI: {e}")
        print(traceback.format_exc())
        messagebox.showerror("Error", f"Error initializing GUI: {str(e)}\n\nCheck console for details.")


if __name__ == "__main__":
    print("Starting Belief Revision GUI...")
    main()
