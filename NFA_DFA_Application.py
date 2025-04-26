import tkinter as tk
from tkinter import scrolledtext, messagebox

class NFAGUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NFA to DFA Converter")
        self.root.configure(bg="black")

        label_style = {"fg": "white", "bg": "black", "font": ("Helvetica", 11, "bold")}
        entry_style = {"bg": "white", "fg": "black", "font": ("Helvetica", 11)}

        # Input fields
        tk.Label(root, text="States (comma-separated):", **label_style).grid(row=0, column=0, columnspan=2, sticky="ew", padx=10)
        self.states_entry = tk.Entry(root, width=60, **entry_style)
        self.states_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        tk.Label(root, text="Alphabet (comma-separated):", **label_style).grid(row=2, column=0, columnspan=2, sticky="ew", padx=10)
        self.alphabet_entry = tk.Entry(root, width=60, **entry_style)
        self.alphabet_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        tk.Label(root, text="Start state:", **label_style).grid(row=4, column=0, columnspan=2, sticky="ew", padx=10)
        self.start_entry = tk.Entry(root, width=60, **entry_style)
        self.start_entry.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        tk.Label(root, text="Final states (comma-separated):", **label_style).grid(row=6, column=0, columnspan=2, sticky="ew", padx=10)
        self.final_entry = tk.Entry(root, width=60, **entry_style)
        self.final_entry.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

        tk.Button(root, text="Set Transitions", command=self.generate_transition_template).grid(row=8, column=0, columnspan=2, pady=10)

        tk.Label(root, text="Transitions (format: state,symbol→state1,state2) ⚠️ Leave empty if there are no transitions.", **label_style).grid(row=9, column=0, columnspan=2, sticky="ew", padx=10)
        self.transitions_text = scrolledtext.ScrolledText(root, width=80, height=6, bg="white", fg="black", font=("Helvetica", 11))
        self.transitions_text.grid(row=10, column=0, columnspan=2, padx=10, pady=5)

        tk.Button(root, text="Convert NFA to DFA", command=self.convert).grid(row=11, column=0, columnspan=2, pady=10)

        self.output = scrolledtext.ScrolledText(root, width=80, height=20, bg="white", fg="black", font=("Helvetica", 11))
        self.output.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

    def generate_transition_template(self):
        states = [s.strip() for s in self.states_entry.get().split(',') if s.strip()]
        alphabet = [s.strip() for s in self.alphabet_entry.get().split(',') if s.strip()]
        states = sorted(set(states))
        alphabet = sorted(set(alphabet))

        if "λ" not in alphabet:
            alphabet.append("λ")
        
        if not states or not alphabet:
            messagebox.showerror("Error", "Please enter valid states and alphabet first.")
            return

        lines = [f"{state},{symbol}→" for state in states for symbol in alphabet]
        self.transitions_text.delete("1.0", tk.END)
        self.transitions_text.insert(tk.END, "\n".join(lines))

    def convert(self):
        states = [s.strip() for s in self.states_entry.get().split(',') if s.strip()]
        alphabet = [s.strip() for s in self.alphabet_entry.get().split(',') if s.strip()]
        start = self.start_entry.get().strip()
        finals = [s.strip() for s in self.final_entry.get().split(',') if s.strip()]

        if not start or start not in states:
            messagebox.showerror("Error", "Start state must be one of the states.")
            return

        transitions_input = self.transitions_text.get("1.0", tk.END).strip()
        transitions = {}

        for i, line in enumerate(transitions_input.split('\n'), 1):
            if '→' not in line:
                continue
            try:
                left, right = line.split('→')
                from_state, symbol = [s.strip() for s in left.split(',')]
                to_states = [s.strip() for s in right.split(',') if s.strip()]
            except ValueError:
                messagebox.showerror("Error", f"Line {i} is malformed: {line}")
                return

            # Validate states and symbols
            if from_state not in states:
                messagebox.showerror("Error", f"Line {i}: State '{from_state}' is not declared.")
                return
            if symbol not in alphabet and symbol != 'λ':
                messagebox.showerror("Error", f"Line {i}: Symbol '{symbol}' is not in the alphabet.")
                return
            for target in to_states:
                if target not in states:
                    messagebox.showerror("Error", f"Line {i}: Destination state '{target}' is not declared.")
                    return

            transitions[(from_state, symbol)] = to_states

        class NFA:
            def __init__(self, states, final_states, start_state, alpha, transitions):
                self.states = states
                self.final_states = final_states
                self.start_states = [start_state]
                self.alpha = alpha
                self.transitions = transitions

            def epsilon_closure(self, state):
                closure = set()
                stack = [state]
                while stack:
                    current = stack.pop()
                    if current not in closure:
                        closure.add(current)
                        epsilon_transitions = self.transitions.get((current, 'λ'), [])
                        for next_state in epsilon_transitions:
                            if next_state not in closure:
                                stack.append(next_state)
                return closure

            def epsilon_closure_set(self, states):
                closure = set()
                for state in states:
                    closure.update(self.epsilon_closure(state))
                return closure

            def move(self, states, symbol):
                next_states = set()
                for state in states:
                    if (state, symbol) in self.transitions:
                        next_states.update(self.transitions[(state, symbol)])
                return next_states

            def nfa_to_dfa(self):
                dfa_states = {}
                dfa_start_state = frozenset(self.epsilon_closure_set(self.start_states))
                dfa_states[dfa_start_state] = {}
                unmarked_states = [dfa_start_state]

                while unmarked_states:
                    current = unmarked_states.pop()
                    for symbol in self.alpha:
                        if symbol == 'λ':
                            continue
                        move_result = self.move(current, symbol)
                        closure_set = set()
                        for state in move_result:
                            closure_set.update(self.epsilon_closure(state))
                        closure_frozenset = frozenset(closure_set)
                        dfa_states[current][symbol] = closure_frozenset
                        if closure_frozenset not in dfa_states:
                            dfa_states[closure_frozenset] = {}
                            unmarked_states.append(closure_frozenset)
                return dfa_states, dfa_start_state

        nfa = NFA(states, finals, start, alphabet, transitions)
        dfa, dfa_start = nfa.nfa_to_dfa()

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, "----- DFA Description -----\n")
        self.output.insert(tk.END, f"Alphabet: {alphabet}\n")
        self.output.insert(tk.END, f"Start State: {set(dfa_start)}\n")
        self.output.insert(tk.END, "Final States:\n")
        for state in dfa:
            if any(s in finals for s in state):
                self.output.insert(tk.END, f"  {set(state)}\n")
        self.output.insert(tk.END, "\nTransitions:\n")
        for state, trans in dfa.items():
            for symbol, target in trans.items():
                self.output.insert(tk.END, f"  δ({set(state)}, '{symbol}') → {set(target)}\n")


# Run the GUI
root = tk.Tk()
app = NFAGUIApp(root)
root.mainloop()