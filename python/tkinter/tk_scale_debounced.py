import tkinter as tk
from tkinter import ttk

class tk_scale_debounced(ttk.Frame):

    """
    scale with after_change event

    aka: debounced scale

    example:

    def after_change(key, value):
        print(key, value)
    root = tk.Tk()
    s = tk_scale_debounced(root, "some label", after_change, "x", from_=-10, to=10)
    s.pack()
    """

    # current value
    value = None

    # debounce timer for keyboard input
    _change_key_timer = None

    def __init__(self, parent, label, after_change, key=None, **scale_kwargs):

        """
        example scale_kwargs:

        from_=-10, to=10, orient='horizontal'
        """

        super().__init__(parent)

        self._after_change = after_change
        self._label = label
        self._key = key or label

        self.value = tk.DoubleVar()

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=100)

        # label
        self._scale_label = ttk.Label(self, text=self._label)
        self._scale_label.grid(column=0, row=0, sticky='w')

        # value
        self._value_label = ttk.Label(self, text=self._format_value())
        self._value_label.grid(column=1, row=0, sticky='w')

        #  scale
        self._scale = ttk.Scale(self, command=self._scale_change_live, variable=self.value, **scale_kwargs)
        self._scale.grid(column=2, row=0, columnspan=4, sticky='we')

        # mouse
        self._scale.bind("<ButtonRelease-1>", self._scale_change_done)
        # keyboard
        self._scale.bind("<KeyRelease>", self._scale_change_key)

    def _format_value(self):
        return '{: .2f}'.format(self.value.get())

    def _scale_change_live(self, event):
        self._value_label.configure(text=self._format_value())

    def _scale_change_done(self, event=None):
        self._after_change(self._key, self.value.get())

    def _scale_change_key(self, event):
        if self._change_key_timer:
            self.after_cancel(self._change_key_timer)
        t = 1000
        self._change_key_timer = self.after(t, self._scale_change_done)
