#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                             HyperFTP v1.0                                     ║
║                    Professional FTP Client for Python                         ║
║                                                                               ║
║  Author: HyperFTP Team                                                        ║
║  License: MIT                                                                 ║
║  Python: 3.8+                                                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import ftplib
import os
import threading
import json
from datetime import datetime
from pathlib import Path
import socket


class HyperFTP:
    """Main FTP Client Application"""
    
    VERSION = "1.0.0"
    APP_NAME = "HyperFTP"
    CONFIG_FILE = "hyperftp_config.json"
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{self.APP_NAME} v{self.VERSION}")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # FTP Connection
        self.ftp = None
        self.connected = False
        self.current_remote_path = "/"
        self.current_local_path = str(Path.home())
        
        # Saved connections
        self.saved_connections = self.load_connections()
        
        # Setup UI
        self.setup_styles()
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.log_message("Welcome to HyperFTP!", "info")
        self.log_message("Enter connection details and click 'Connect' to start.", "info")
        self.refresh_local_files()

    def setup_styles(self):
        """Configure modern dark theme styles using 60-30-10 color rule"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # ============================================================
        # MINIMALIST BLACK & WHITE THEME
        # ============================================================
        # Only 2 colors: Black (#0a0a0a) and White (#ffffff)
        # Clean, professional, distraction-free
        # ============================================================
        
        BLACK = '#0a0a0a'
        WHITE = '#ffffff'
        GRAY = '#1a1a1a'      # Slightly lighter black for cards
        LIGHT_GRAY = '#2a2a2a'  # For borders/hover
        
        self.colors = {
            # Backgrounds
            'dominant': BLACK,
            'dominant_alt': BLACK,
            'secondary': GRAY,
            'secondary_light': LIGHT_GRAY,
            'secondary_border': LIGHT_GRAY,
            
            # Accent = White
            'accent': WHITE,
            'accent_hover': '#e0e0e0',
            'accent_muted': '#cccccc',
            
            # Semantic (all white-based)
            'success': WHITE,
            'success_hover': '#e0e0e0',
            'danger': WHITE,
            'danger_hover': '#e0e0e0',
            'warning': WHITE,
            
            # Text = White
            'text_primary': WHITE,
            'text_secondary': '#b0b0b0',
            'text_muted': '#707070',
            'text_on_accent': BLACK,
            
            # Borders
            'border': LIGHT_GRAY,
            'border_light': '#3a3a3a',
            'border_muted': GRAY,
        }
        
        # Configure root window (60% DOMINANT)
        self.root.configure(bg=self.colors['dominant'])
        
        # ==================== FRAME STYLES (60% DOMINANT) ====================
        self.style.configure('TFrame',
                           background=self.colors['dominant'])
        
        self.style.configure('Card.TFrame',
                           background=self.colors['secondary'],
                           relief='flat')
        
        # ==================== LABEL STYLES ====================
        self.style.configure('TLabel',
                           background=self.colors['dominant'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10))
        
        self.style.configure('Header.TLabel',
                           background=self.colors['dominant'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('Muted.TLabel',
                           background=self.colors['dominant'],
                           foreground=self.colors['text_muted'],
                           font=('Segoe UI', 9))
        
        # ==================== BUTTON STYLES (10% ACCENT for Primary) ====================
        # Primary Button - Uses ACCENT color (10%)
        self.style.configure('Primary.TButton',
                           background=self.colors['accent'],
                           foreground=self.colors['dominant'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8),
                           borderwidth=0)
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent_muted'])])
        
        # Success Button - Semantic accent (within 10%)
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground=self.colors['dominant'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8),
                           borderwidth=0)
        self.style.map('Success.TButton',
                      background=[('active', self.colors['success_hover']),
                                ('pressed', self.colors['success']),
                                ('disabled', self.colors['secondary_light'])])
        
        # Danger Button - Semantic accent (within 10%)
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground=self.colors['text_on_accent'],
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8),
                           borderwidth=0)
        self.style.map('Danger.TButton',
                      background=[('active', self.colors['danger_hover']),
                                ('pressed', self.colors['danger']),
                                ('disabled', self.colors['secondary_light'])])
        
        # Secondary Button (30% SECONDARY) - Uses secondary colors
        self.style.configure('Secondary.TButton',
                           background=self.colors['secondary_light'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10),
                           padding=(12, 6),
                           borderwidth=1)
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['accent']),
                                ('pressed', self.colors['accent_muted'])])
        
        # Toolbar Button (30% SECONDARY)
        self.style.configure('Toolbar.TButton',
                           background=self.colors['secondary'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 9),
                           padding=(10, 6),
                           borderwidth=1)
        self.style.map('Toolbar.TButton',
                      background=[('active', self.colors['secondary_light']),
                                ('pressed', self.colors['accent'])])
        
        # Icon Button (30% SECONDARY)
        self.style.configure('Icon.TButton',
                           background=self.colors['secondary'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 11),
                           padding=(8, 4),
                           borderwidth=0)
        self.style.map('Icon.TButton',
                      background=[('active', self.colors['secondary_light'])])
        
        # ==================== ENTRY STYLES (30% SECONDARY) ====================
        self.style.configure('TEntry',
                           fieldbackground=self.colors['secondary'],
                           foreground=self.colors['text_primary'],
                           insertcolor=self.colors['accent'],
                           borderwidth=1,
                           relief='flat',
                           padding=(8, 6))
        self.style.map('TEntry',
                      fieldbackground=[('focus', self.colors['secondary_light'])],
                      bordercolor=[('focus', self.colors['accent'])])
        
        # ==================== COMBOBOX STYLES (30% SECONDARY) ====================
        self.style.configure('TCombobox',
                           fieldbackground=self.colors['secondary'],
                           background=self.colors['secondary'],
                           foreground=self.colors['text_primary'],
                           arrowcolor=self.colors['accent'],
                           borderwidth=1,
                           padding=(8, 6))
        self.style.map('TCombobox',
                      fieldbackground=[('focus', self.colors['secondary_light'])],
                      background=[('active', self.colors['secondary_light'])])
        
        # ==================== CHECKBOX STYLES (60% DOMINANT bg) ====================
        self.style.configure('TCheckbutton',
                           background=self.colors['dominant'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 10))
        self.style.map('TCheckbutton',
                      background=[('active', self.colors['dominant'])])
        
        # ==================== LABELFRAME STYLES ====================
        # Main LabelFrame (60% DOMINANT)
        self.style.configure('TLabelframe',
                           background=self.colors['dominant'],
                           foreground=self.colors['accent'],
                           bordercolor=self.colors['border'],
                           relief='solid',
                           borderwidth=1)
        self.style.configure('TLabelframe.Label',
                           background=self.colors['dominant'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 11, 'bold'))
        
        # Card LabelFrame (30% SECONDARY)
        self.style.configure('Card.TLabelframe',
                           background=self.colors['secondary'],
                           foreground=self.colors['accent'],
                           bordercolor=self.colors['border_light'],
                           relief='solid',
                           borderwidth=1)
        self.style.configure('Card.TLabelframe.Label',
                           background=self.colors['secondary'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 11, 'bold'))
        
        # ==================== TREEVIEW STYLES (30% SECONDARY) ====================
        self.style.configure('Treeview',
                           background=self.colors['secondary'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['secondary'],
                           borderwidth=0,
                           font=('Segoe UI', 10),
                           rowheight=28)
        self.style.configure('Treeview.Heading',
                           background=self.colors['secondary_light'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=0,
                           relief='flat')
        # Selection uses 10% ACCENT
        self.style.map('Treeview',
                      background=[('selected', self.colors['accent'])],
                      foreground=[('selected', self.colors['dominant'])])
        self.style.map('Treeview.Heading',
                      background=[('active', self.colors['accent'])])
        
        # ==================== SCROLLBAR STYLES ====================
        self.style.configure('Vertical.TScrollbar',
                           background=self.colors['secondary_light'],
                           troughcolor=self.colors['dominant'],
                           bordercolor=self.colors['dominant'],
                           arrowcolor=self.colors['accent'],
                           width=10)
        self.style.map('Vertical.TScrollbar',
                      background=[('active', self.colors['accent']),
                                ('pressed', self.colors['accent_hover'])])
        
        self.style.configure('Horizontal.TScrollbar',
                           background=self.colors['secondary_light'],
                           troughcolor=self.colors['dominant'],
                           bordercolor=self.colors['dominant'],
                           arrowcolor=self.colors['accent'],
                           width=10)
        
        # ==================== PROGRESSBAR STYLES (10% ACCENT) ====================
        self.style.configure('Horizontal.TProgressbar',
                           background=self.colors['accent'],
                           troughcolor=self.colors['secondary'],
                           bordercolor=self.colors['border'],
                           lightcolor=self.colors['accent'],
                           darkcolor=self.colors['accent_muted'])
        
        # ==================== PANEDWINDOW STYLES (60% DOMINANT) ====================
        self.style.configure('TPanedwindow',
                           background=self.colors['dominant'])
        
        # ==================== NOTEBOOK STYLES ====================
        self.style.configure('TNotebook',
                           background=self.colors['dominant'],
                           borderwidth=0)
        self.style.configure('TNotebook.Tab',
                           background=self.colors['secondary'],
                           foreground=self.colors['text_secondary'],
                           padding=(15, 8),
                           font=('Segoe UI', 10))
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.colors['accent'])],
                      foreground=[('selected', self.colors['dominant'])])
        
        # ==================== STATUS BAR STYLE ====================
        self.style.configure('Status.TLabel',
                           background=self.colors['dominant_alt'],
                           foreground=self.colors['accent'],
                           font=('Segoe UI', 10),
                           padding=(10, 5))
        
        self.style.configure('StatusBar.TFrame',
                           background=self.colors['dominant_alt'])

    def create_menu(self):
        """Create application menu bar with black & white theme"""
        # Black and white menu colors
        menu_bg = '#1a1a1a'
        menu_fg = '#ffffff'
        menu_active_bg = '#ffffff'
        menu_active_fg = '#0a0a0a'
        
        menubar = tk.Menu(self.root, 
                         bg=menu_bg, 
                         fg=menu_fg,
                         activebackground=menu_active_bg,
                         activeforeground=menu_active_fg,
                         borderwidth=0,
                         relief='flat')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0,
                           bg=menu_bg, fg=menu_fg,
                           activebackground=menu_active_bg,
                           activeforeground=menu_active_fg)
        menubar.add_cascade(label="  File  ", menu=file_menu)
        file_menu.add_command(label="  📄 New Connection", command=self.new_connection, accelerator="Ctrl+N")
        file_menu.add_command(label="  💾 Save Connection", command=self.save_current_connection)
        file_menu.add_separator()
        file_menu.add_command(label="  🚪 Exit", command=self.on_closing, accelerator="Alt+F4")
        
        # Transfer menu
        transfer_menu = tk.Menu(menubar, tearoff=0,
                               bg=menu_bg, fg=menu_fg,
                               activebackground=menu_active_bg,
                               activeforeground=menu_active_fg)
        menubar.add_cascade(label="  Transfer  ", menu=transfer_menu)
        transfer_menu.add_command(label="  ⬆️ Upload", command=self.upload_file, accelerator="Ctrl+U")
        transfer_menu.add_command(label="  ⬇️ Download", command=self.download_file, accelerator="Ctrl+D")
        transfer_menu.add_separator()
        transfer_menu.add_command(label="  📁 Upload Folder", command=self.upload_folder)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0,
                           bg=menu_bg, fg=menu_fg,
                           activebackground=menu_active_bg,
                           activeforeground=menu_active_fg)
        menubar.add_cascade(label="  View  ", menu=view_menu)
        view_menu.add_command(label="  🔄 Refresh Local", command=self.refresh_local_files, accelerator="F5")
        view_menu.add_command(label="  🔄 Refresh Remote", command=self.refresh_remote_files, accelerator="F6")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0,
                           bg=menu_bg, fg=menu_fg,
                           activebackground=menu_active_bg,
                           activeforeground=menu_active_fg)
        menubar.add_cascade(label="  Help  ", menu=help_menu)
        help_menu.add_command(label="  ℹ️ About", command=self.show_about)
        help_menu.add_command(label="  📖 Documentation", command=self.show_docs)
        
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_connection())
        self.root.bind('<Control-u>', lambda e: self.upload_file())
        self.root.bind('<Control-d>', lambda e: self.download_file())
        self.root.bind('<F5>', lambda e: self.refresh_local_files())
        self.root.bind('<F6>', lambda e: self.refresh_remote_files())

    def create_toolbar(self):
        """Create main toolbar"""
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(toolbar, text="Connection", padding="5")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Row 1: Host and Port
        row1 = ttk.Frame(conn_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Label(row1, text="Host:").pack(side=tk.LEFT, padx=(0, 5))
        self.host_var = tk.StringVar(value="")
        self.host_entry = ttk.Entry(row1, textvariable=self.host_var, width=30)
        self.host_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row1, text="Port:").pack(side=tk.LEFT, padx=(0, 5))
        self.port_var = tk.StringVar(value="21")
        self.port_entry = ttk.Entry(row1, textvariable=self.port_var, width=6)
        self.port_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row1, text="Saved:").pack(side=tk.LEFT, padx=(0, 5))
        self.saved_conn_var = tk.StringVar()
        self.saved_combo = ttk.Combobox(row1, textvariable=self.saved_conn_var, 
                                        values=list(self.saved_connections.keys()), width=20)
        self.saved_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.saved_combo.bind('<<ComboboxSelected>>', self.load_saved_connection)
        
        # Row 2: Username and Password
        row2 = ttk.Frame(conn_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Label(row2, text="Username:").pack(side=tk.LEFT, padx=(0, 5))
        self.user_var = tk.StringVar(value="")
        self.user_entry = ttk.Entry(row2, textvariable=self.user_var, width=20)
        self.user_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(row2, text="Password:").pack(side=tk.LEFT, padx=(0, 5))
        self.pass_var = tk.StringVar(value="")
        self.pass_entry = ttk.Entry(row2, textvariable=self.pass_var, width=20, show="●")
        self.pass_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Anonymous checkbox
        self.anonymous_var = tk.BooleanVar(value=False)
        self.anonymous_check = ttk.Checkbutton(row2, text="Anonymous", 
                                                variable=self.anonymous_var,
                                                command=self.toggle_anonymous)
        self.anonymous_check.pack(side=tk.LEFT, padx=(0, 15))
        
        # TLS/SSL checkbox
        self.tls_var = tk.BooleanVar(value=False)
        self.tls_check = ttk.Checkbutton(row2, text="TLS/SSL", variable=self.tls_var)
        self.tls_check.pack(side=tk.LEFT, padx=(0, 15))
        
        # Passive mode checkbox
        self.passive_var = tk.BooleanVar(value=True)
        self.passive_check = ttk.Checkbutton(row2, text="Passive Mode", variable=self.passive_var)
        self.passive_check.pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="🔌 Connect", 
                                      command=self.connect_ftp, style='Success.TButton')
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.disconnect_btn = ttk.Button(btn_frame, text="❌ Disconnect", 
                                         command=self.disconnect_ftp, style='Danger.TButton',
                                         state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="💾 Save Connection", 
                  command=self.save_current_connection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Delete Saved", 
                  command=self.delete_saved_connection).pack(side=tk.LEFT, padx=5)

    def create_main_layout(self):
        """Create main file browser layout"""
        # Main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Local files
        left_frame = ttk.LabelFrame(main_paned, text="📁 Local Files", padding="5")
        main_paned.add(left_frame, weight=1)
        
        # Local path bar
        local_path_frame = ttk.Frame(left_frame)
        local_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(local_path_frame, text="Path:").pack(side=tk.LEFT)
        self.local_path_var = tk.StringVar(value=self.current_local_path)
        self.local_path_entry = ttk.Entry(local_path_frame, textvariable=self.local_path_var)
        self.local_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.local_path_entry.bind('<Return>', lambda e: self.navigate_local_path())
        
        ttk.Button(local_path_frame, text="📂", width=3,
                  command=self.browse_local_folder).pack(side=tk.LEFT)
        ttk.Button(local_path_frame, text="⬆️", width=3,
                  command=self.local_go_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(local_path_frame, text="🔄", width=3,
                  command=self.refresh_local_files).pack(side=tk.LEFT)
        
        # Local file list
        local_tree_frame = ttk.Frame(left_frame)
        local_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.local_tree = ttk.Treeview(local_tree_frame, 
                                       columns=('name', 'size', 'modified'),
                                       show='headings', selectmode='extended')
        self.local_tree.heading('name', text='Name', anchor=tk.W)
        self.local_tree.heading('size', text='Size', anchor=tk.E)
        self.local_tree.heading('modified', text='Modified', anchor=tk.W)
        self.local_tree.column('name', width=200)
        self.local_tree.column('size', width=80)
        self.local_tree.column('modified', width=120)
        
        local_scroll_y = ttk.Scrollbar(local_tree_frame, orient=tk.VERTICAL, 
                                       command=self.local_tree.yview)
        local_scroll_x = ttk.Scrollbar(local_tree_frame, orient=tk.HORIZONTAL,
                                       command=self.local_tree.xview)
        self.local_tree.configure(yscrollcommand=local_scroll_y.set,
                                 xscrollcommand=local_scroll_x.set)
        
        self.local_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        local_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.local_tree.bind('<Double-1>', self.local_double_click)
        self.local_tree.bind('<Button-3>', self.local_context_menu)
        
        # Local buttons
        local_btn_frame = ttk.Frame(left_frame)
        local_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(local_btn_frame, text="⬆️ Upload", 
                  command=self.upload_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(local_btn_frame, text="📁 New Folder",
                  command=self.create_local_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(local_btn_frame, text="🗑️ Delete",
                  command=self.delete_local_file).pack(side=tk.LEFT, padx=2)
        
        # Right panel - Remote files
        right_frame = ttk.LabelFrame(main_paned, text="🌐 Remote Files", padding="5")
        main_paned.add(right_frame, weight=1)
        
        # Remote path bar
        remote_path_frame = ttk.Frame(right_frame)
        remote_path_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(remote_path_frame, text="Path:").pack(side=tk.LEFT)
        self.remote_path_var = tk.StringVar(value="/")
        self.remote_path_entry = ttk.Entry(remote_path_frame, textvariable=self.remote_path_var)
        self.remote_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.remote_path_entry.bind('<Return>', lambda e: self.navigate_remote_path())
        
        ttk.Button(remote_path_frame, text="⬆️", width=3,
                  command=self.remote_go_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(remote_path_frame, text="🔄", width=3,
                  command=self.refresh_remote_files).pack(side=tk.LEFT)
        
        # Remote file list
        remote_tree_frame = ttk.Frame(right_frame)
        remote_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.remote_tree = ttk.Treeview(remote_tree_frame,
                                        columns=('name', 'size', 'modified'),
                                        show='headings', selectmode='extended')
        self.remote_tree.heading('name', text='Name', anchor=tk.W)
        self.remote_tree.heading('size', text='Size', anchor=tk.E)
        self.remote_tree.heading('modified', text='Modified', anchor=tk.W)
        self.remote_tree.column('name', width=200)
        self.remote_tree.column('size', width=80)
        self.remote_tree.column('modified', width=120)
        
        remote_scroll_y = ttk.Scrollbar(remote_tree_frame, orient=tk.VERTICAL,
                                        command=self.remote_tree.yview)
        remote_scroll_x = ttk.Scrollbar(remote_tree_frame, orient=tk.HORIZONTAL,
                                        command=self.remote_tree.xview)
        self.remote_tree.configure(yscrollcommand=remote_scroll_y.set,
                                  xscrollcommand=remote_scroll_x.set)
        
        self.remote_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        remote_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.remote_tree.bind('<Double-1>', self.remote_double_click)
        self.remote_tree.bind('<Button-3>', self.remote_context_menu)
        
        # Remote buttons
        remote_btn_frame = ttk.Frame(right_frame)
        remote_btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(remote_btn_frame, text="⬇️ Download",
                  command=self.download_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(remote_btn_frame, text="📁 New Folder",
                  command=self.create_remote_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(remote_btn_frame, text="🗑️ Delete",
                  command=self.delete_remote_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(remote_btn_frame, text="✏️ Rename",
                  command=self.rename_remote_file).pack(side=tk.LEFT, padx=2)
        
        # Log panel at bottom
        log_frame = ttk.LabelFrame(self.root, text="📋 Transfer Log", padding="5")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, 
                                                  font=('Consolas', 10),
                                                  bg='#313244',           # Surface0
                                                  fg='#a6adc8',           # Subtext1
                                                  insertbackground='#cba6f7',  # Mauve
                                                  selectbackground='#cba6f7',  # Mauve
                                                  selectforeground='#1e1e2e',  # Base
                                                  relief='flat',
                                                  padx=10,
                                                  pady=8,
                                                  state=tk.DISABLED)
        self.log_text.pack(fill=tk.X)
        
        # Configure log tags with Catppuccin colors
        self.log_text.tag_configure('info', foreground='#89b4fa')     # Blue
        self.log_text.tag_configure('success', foreground='#a6e3a1')  # Green
        self.log_text.tag_configure('error', foreground='#f38ba8')    # Red
        self.log_text.tag_configure('warning', foreground='#fab387')  # Peach

    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                      style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                            length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)

    # ==================== CONNECTION METHODS ====================
    
    def connect_ftp(self):
        """Connect to FTP server"""
        host = self.host_var.get().strip()
        port = int(self.port_var.get() or 21)
        username = self.user_var.get().strip()
        password = self.pass_var.get()
        
        if not host:
            messagebox.showerror("Error", "Please enter a host address")
            return
        
        if self.anonymous_var.get():
            username = "anonymous"
            password = "anonymous@"
        elif not username:
            messagebox.showerror("Error", "Please enter username or check Anonymous")
            return
        
        self.log_message(f"Connecting to {host}:{port}...", "info")
        self.status_var.set(f"Connecting to {host}...")
        
        # Connect in thread to avoid GUI freeze
        thread = threading.Thread(target=self._connect_thread, 
                                 args=(host, port, username, password))
        thread.daemon = True
        thread.start()

    def _connect_thread(self, host, port, username, password):
        """Thread for FTP connection"""
        try:
            if self.tls_var.get():
                self.ftp = ftplib.FTP_TLS()
            else:
                self.ftp = ftplib.FTP()
            
            self.ftp.connect(host, port, timeout=30)
            self.ftp.login(username, password)
            
            if self.tls_var.get():
                self.ftp.prot_p()  # Switch to secure data connection
            
            if self.passive_var.get():
                self.ftp.set_pasv(True)
            
            self.connected = True
            self.current_remote_path = self.ftp.pwd()
            
            self.root.after(0, self._on_connect_success)
            
        except Exception as e:
            self.root.after(0, lambda: self._on_connect_error(str(e)))

    def _on_connect_success(self):
        """Called when connection succeeds"""
        self.log_message(f"Connected successfully! Welcome: {self.ftp.getwelcome()}", "success")
        self.status_var.set(f"Connected to {self.host_var.get()}")
        self.connect_btn.config(state=tk.DISABLED)
        self.disconnect_btn.config(state=tk.NORMAL)
        self.refresh_remote_files()

    def _on_connect_error(self, error):
        """Called when connection fails"""
        self.log_message(f"Connection failed: {error}", "error")
        self.status_var.set("Connection failed")
        messagebox.showerror("Connection Error", f"Failed to connect:\n{error}")
        self.ftp = None
        self.connected = False

    def disconnect_ftp(self):
        """Disconnect from FTP server"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
        
        self.connected = False
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.remote_tree.delete(*self.remote_tree.get_children())
        self.remote_path_var.set("/")
        self.status_var.set("Disconnected")
        self.log_message("Disconnected from server", "info")

    # ==================== FILE OPERATIONS ====================
    
    def refresh_local_files(self):
        """Refresh local file list"""
        self.local_tree.delete(*self.local_tree.get_children())
        
        try:
            path = self.current_local_path
            self.local_path_var.set(path)
            
            # List directory contents
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                try:
                    stat = os.stat(full_path)
                    is_dir = os.path.isdir(full_path)
                    size = "" if is_dir else self.format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    prefix = "📁 " if is_dir else "📄 "
                    items.append((is_dir, item, prefix + item, size, modified))
                except PermissionError:
                    items.append((False, item, "🔒 " + item, "", "Access Denied"))
            
            # Sort: folders first, then files
            items.sort(key=lambda x: (not x[0], x[1].lower()))
            
            for is_dir, name, display_name, size, modified in items:
                item_id = self.local_tree.insert('', 'end', values=(display_name, size, modified))
                self.local_tree.item(item_id, tags=('folder' if is_dir else 'file',))
                
        except Exception as e:
            self.log_message(f"Error reading local directory: {e}", "error")

    def refresh_remote_files(self):
        """Refresh remote file list"""
        if not self.connected:
            return
        
        self.remote_tree.delete(*self.remote_tree.get_children())
        
        try:
            self.remote_path_var.set(self.current_remote_path)
            
            # Get file listing
            items = []
            self.ftp.cwd(self.current_remote_path)
            
            try:
                # Try MLSD (modern)
                for name, facts in self.ftp.mlsd():
                    if name in ['.', '..']:
                        continue
                    is_dir = facts.get('type') == 'dir'
                    size = "" if is_dir else self.format_size(int(facts.get('size', 0)))
                    modify = facts.get('modify', '')
                    if modify:
                        try:
                            modified = datetime.strptime(modify[:14], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M')
                        except:
                            modified = modify
                    else:
                        modified = ""
                    prefix = "📁 " if is_dir else "📄 "
                    items.append((is_dir, name, prefix + name, size, modified))
            except:
                # Fallback to LIST
                lines = []
                self.ftp.dir(lines.append)
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        is_dir = line.startswith('d')
                        name = ' '.join(parts[8:])
                        size = "" if is_dir else self.format_size(int(parts[4]))
                        modified = ' '.join(parts[5:8])
                        prefix = "📁 " if is_dir else "📄 "
                        items.append((is_dir, name, prefix + name, size, modified))
            
            # Sort: folders first
            items.sort(key=lambda x: (not x[0], x[1].lower()))
            
            for is_dir, name, display_name, size, modified in items:
                item_id = self.remote_tree.insert('', 'end', values=(display_name, size, modified))
                self.remote_tree.item(item_id, tags=('folder' if is_dir else 'file',))
                
            self.log_message(f"Loaded {len(items)} items from remote", "info")
            
        except Exception as e:
            self.log_message(f"Error reading remote directory: {e}", "error")

    def upload_file(self):
        """Upload selected local files"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        selected = self.local_tree.selection()
        if not selected:
            # No selection, open file dialog
            files = filedialog.askopenfilenames(
                title="Select files to upload",
                initialdir=self.current_local_path
            )
            if files:
                for file_path in files:
                    self._upload_single_file(file_path)
        else:
            for item in selected:
                values = self.local_tree.item(item)['values']
                name = values[0].replace("📁 ", "").replace("📄 ", "").replace("🔒 ", "")
                local_path = os.path.join(self.current_local_path, name)
                
                if os.path.isfile(local_path):
                    self._upload_single_file(local_path)
                elif os.path.isdir(local_path):
                    self._upload_folder(local_path, name)

    def _upload_single_file(self, file_path):
        """Upload a single file"""
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        self.log_message(f"Uploading: {filename} ({self.format_size(file_size)})", "info")
        self.status_var.set(f"Uploading: {filename}")
        
        def upload_thread():
            try:
                uploaded = [0]
                
                def callback(data):
                    uploaded[0] += len(data)
                    progress = (uploaded[0] / file_size) * 100
                    self.root.after(0, lambda: self.progress_var.set(progress))
                
                with open(file_path, 'rb') as f:
                    self.ftp.storbinary(f'STOR {filename}', f, 8192, callback)
                
                self.root.after(0, lambda: self._upload_complete(filename))
                
            except Exception as e:
                self.root.after(0, lambda: self._upload_error(filename, str(e)))
        
        thread = threading.Thread(target=upload_thread)
        thread.daemon = True
        thread.start()

    def _upload_complete(self, filename):
        """Called when upload completes"""
        self.log_message(f"Upload complete: {filename}", "success")
        self.status_var.set("Upload complete")
        self.progress_var.set(0)
        self.refresh_remote_files()

    def _upload_error(self, filename, error):
        """Called when upload fails"""
        self.log_message(f"Upload failed: {filename} - {error}", "error")
        self.status_var.set("Upload failed")
        self.progress_var.set(0)

    def download_file(self):
        """Download selected remote files"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server")
            return
        
        selected = self.remote_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select files to download")
            return
        
        for item in selected:
            values = self.remote_tree.item(item)['values']
            name = values[0].replace("📁 ", "").replace("📄 ", "")
            tags = self.remote_tree.item(item)['tags']
            
            if 'folder' not in tags:
                self._download_single_file(name)

    def _download_single_file(self, filename):
        """Download a single file"""
        local_path = os.path.join(self.current_local_path, filename)
        
        self.log_message(f"Downloading: {filename}", "info")
        self.status_var.set(f"Downloading: {filename}")
        
        def download_thread():
            try:
                # Get file size
                try:
                    file_size = self.ftp.size(filename)
                except:
                    file_size = 0
                
                downloaded = [0]
                
                def callback(data):
                    downloaded[0] += len(data)
                    if file_size > 0:
                        progress = (downloaded[0] / file_size) * 100
                        self.root.after(0, lambda: self.progress_var.set(progress))
                    return data
                
                with open(local_path, 'wb') as f:
                    def write_callback(data):
                        callback(data)
                        f.write(data)
                    
                    self.ftp.retrbinary(f'RETR {filename}', write_callback, 8192)
                
                self.root.after(0, lambda: self._download_complete(filename))
                
            except Exception as e:
                self.root.after(0, lambda: self._download_error(filename, str(e)))
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

    def _download_complete(self, filename):
        """Called when download completes"""
        self.log_message(f"Download complete: {filename}", "success")
        self.status_var.set("Download complete")
        self.progress_var.set(0)
        self.refresh_local_files()

    def _download_error(self, filename, error):
        """Called when download fails"""
        self.log_message(f"Download failed: {filename} - {error}", "error")
        self.status_var.set("Download failed")
        self.progress_var.set(0)

    # ==================== NAVIGATION ====================
    
    def local_double_click(self, event):
        """Handle double click on local file list"""
        selected = self.local_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.local_tree.item(item)['values']
        name = values[0].replace("📁 ", "").replace("📄 ", "").replace("🔒 ", "")
        path = os.path.join(self.current_local_path, name)
        
        if os.path.isdir(path):
            self.current_local_path = path
            self.refresh_local_files()

    def remote_double_click(self, event):
        """Handle double click on remote file list"""
        if not self.connected:
            return
        
        selected = self.remote_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.remote_tree.item(item)['values']
        name = values[0].replace("📁 ", "").replace("📄 ", "")
        tags = self.remote_tree.item(item)['tags']
        
        if 'folder' in tags:
            try:
                new_path = self.current_remote_path.rstrip('/') + '/' + name
                self.ftp.cwd(new_path)
                self.current_remote_path = self.ftp.pwd()
                self.refresh_remote_files()
            except Exception as e:
                self.log_message(f"Cannot enter directory: {e}", "error")

    def local_go_up(self):
        """Go to parent local directory"""
        parent = os.path.dirname(self.current_local_path)
        if parent and os.path.exists(parent):
            self.current_local_path = parent
            self.refresh_local_files()

    def remote_go_up(self):
        """Go to parent remote directory"""
        if not self.connected:
            return
        
        try:
            self.ftp.cwd('..')
            self.current_remote_path = self.ftp.pwd()
            self.refresh_remote_files()
        except Exception as e:
            self.log_message(f"Cannot go up: {e}", "error")

    def navigate_local_path(self):
        """Navigate to entered local path"""
        path = self.local_path_var.get()
        if os.path.isdir(path):
            self.current_local_path = path
            self.refresh_local_files()
        else:
            messagebox.showerror("Error", "Invalid path")

    def navigate_remote_path(self):
        """Navigate to entered remote path"""
        if not self.connected:
            return
        
        path = self.remote_path_var.get()
        try:
            self.ftp.cwd(path)
            self.current_remote_path = self.ftp.pwd()
            self.refresh_remote_files()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot navigate to path: {e}")

    def browse_local_folder(self):
        """Browse for local folder"""
        folder = filedialog.askdirectory(initialdir=self.current_local_path)
        if folder:
            self.current_local_path = folder
            self.refresh_local_files()

    # ==================== FILE MANAGEMENT ====================
    
    def create_local_folder(self):
        """Create new local folder"""
        from tkinter import simpledialog
        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            path = os.path.join(self.current_local_path, name)
            try:
                os.makedirs(path)
                self.refresh_local_files()
                self.log_message(f"Created local folder: {name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {e}")

    def create_remote_folder(self):
        """Create new remote folder"""
        if not self.connected:
            return
        
        from tkinter import simpledialog
        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            try:
                self.ftp.mkd(name)
                self.refresh_remote_files()
                self.log_message(f"Created remote folder: {name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {e}")

    def delete_local_file(self):
        """Delete selected local files"""
        selected = self.local_tree.selection()
        if not selected:
            return
        
        if not messagebox.askyesno("Confirm Delete", "Delete selected files?"):
            return
        
        for item in selected:
            values = self.local_tree.item(item)['values']
            name = values[0].replace("📁 ", "").replace("📄 ", "").replace("🔒 ", "")
            path = os.path.join(self.current_local_path, name)
            
            try:
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.log_message(f"Deleted: {name}", "success")
            except Exception as e:
                self.log_message(f"Cannot delete {name}: {e}", "error")
        
        self.refresh_local_files()

    def delete_remote_file(self):
        """Delete selected remote files"""
        if not self.connected:
            return
        
        selected = self.remote_tree.selection()
        if not selected:
            return
        
        if not messagebox.askyesno("Confirm Delete", "Delete selected files from server?"):
            return
        
        for item in selected:
            values = self.remote_tree.item(item)['values']
            name = values[0].replace("📁 ", "").replace("📄 ", "")
            tags = self.remote_tree.item(item)['tags']
            
            try:
                if 'folder' in tags:
                    self.ftp.rmd(name)
                else:
                    self.ftp.delete(name)
                self.log_message(f"Deleted: {name}", "success")
            except Exception as e:
                self.log_message(f"Cannot delete {name}: {e}", "error")
        
        self.refresh_remote_files()

    def rename_remote_file(self):
        """Rename remote file"""
        if not self.connected:
            return
        
        selected = self.remote_tree.selection()
        if not selected:
            return
        
        values = self.remote_tree.item(selected[0])['values']
        old_name = values[0].replace("📁 ", "").replace("📄 ", "")
        
        from tkinter import simpledialog
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        
        if new_name and new_name != old_name:
            try:
                self.ftp.rename(old_name, new_name)
                self.refresh_remote_files()
                self.log_message(f"Renamed: {old_name} -> {new_name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot rename: {e}")

    # ==================== CONTEXT MENUS ====================
    
    def local_context_menu(self, event):
        """Show local file context menu with Catppuccin theme"""
        menu = tk.Menu(self.root, tearoff=0,
                      bg='#313244', fg='#cdd6f4',           # Surface0, Text
                      activebackground='#cba6f7', activeforeground='#1e1e2e')  # Mauve, Base
        menu.add_command(label="  ⬆️ Upload", command=self.upload_file)
        menu.add_command(label="  📁 New Folder", command=self.create_local_folder)
        menu.add_command(label="  🗑️ Delete", command=self.delete_local_file)
        menu.add_separator()
        menu.add_command(label="  🔄 Refresh", command=self.refresh_local_files)
        menu.tk_popup(event.x_root, event.y_root)

    def remote_context_menu(self, event):
        """Show remote file context menu with Catppuccin theme"""
        if not self.connected:
            return
        
        menu = tk.Menu(self.root, tearoff=0,
                      bg='#313244', fg='#cdd6f4',           # Surface0, Text
                      activebackground='#cba6f7', activeforeground='#1e1e2e')  # Mauve, Base
        menu.add_command(label="  ⬇️ Download", command=self.download_file)
        menu.add_command(label="  📁 New Folder", command=self.create_remote_folder)
        menu.add_command(label="  ✏️ Rename", command=self.rename_remote_file)
        menu.add_command(label="  🗑️ Delete", command=self.delete_remote_file)
        menu.add_separator()
        menu.add_command(label="  🔄 Refresh", command=self.refresh_remote_files)
        menu.tk_popup(event.x_root, event.y_root)

    # ==================== CONNECTION MANAGEMENT ====================
    
    def load_connections(self):
        """Load saved connections from config file"""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_connections(self):
        """Save connections to config file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.saved_connections, f, indent=2)
        except Exception as e:
            self.log_message(f"Cannot save connections: {e}", "error")

    def save_current_connection(self):
        """Save current connection settings"""
        from tkinter import simpledialog
        name = simpledialog.askstring("Save Connection", "Enter connection name:")
        
        if name:
            self.saved_connections[name] = {
                'host': self.host_var.get(),
                'port': self.port_var.get(),
                'username': self.user_var.get(),
                'password': self.pass_var.get(),
                'anonymous': self.anonymous_var.get(),
                'tls': self.tls_var.get(),
                'passive': self.passive_var.get()
            }
            self.save_connections()
            self.saved_combo['values'] = list(self.saved_connections.keys())
            self.log_message(f"Connection saved: {name}", "success")

    def load_saved_connection(self, event=None):
        """Load a saved connection"""
        name = self.saved_conn_var.get()
        if name in self.saved_connections:
            conn = self.saved_connections[name]
            self.host_var.set(conn.get('host', ''))
            self.port_var.set(conn.get('port', '21'))
            self.user_var.set(conn.get('username', ''))
            self.pass_var.set(conn.get('password', ''))
            self.anonymous_var.set(conn.get('anonymous', False))
            self.tls_var.set(conn.get('tls', False))
            self.passive_var.set(conn.get('passive', True))
            self.toggle_anonymous()
            self.log_message(f"Loaded connection: {name}", "info")

    def delete_saved_connection(self):
        """Delete a saved connection"""
        name = self.saved_conn_var.get()
        if name and name in self.saved_connections:
            if messagebox.askyesno("Confirm", f"Delete connection '{name}'?"):
                del self.saved_connections[name]
                self.save_connections()
                self.saved_combo['values'] = list(self.saved_connections.keys())
                self.saved_conn_var.set('')
                self.log_message(f"Deleted connection: {name}", "success")

    def new_connection(self):
        """Clear form for new connection"""
        self.host_var.set('')
        self.port_var.set('21')
        self.user_var.set('')
        self.pass_var.set('')
        self.anonymous_var.set(False)
        self.tls_var.set(False)
        self.passive_var.set(True)
        self.saved_conn_var.set('')
        self.toggle_anonymous()

    def toggle_anonymous(self):
        """Toggle anonymous login"""
        if self.anonymous_var.get():
            self.user_entry.config(state=tk.DISABLED)
            self.pass_entry.config(state=tk.DISABLED)
        else:
            self.user_entry.config(state=tk.NORMAL)
            self.pass_entry.config(state=tk.NORMAL)

    # ==================== UTILITIES ====================
    
    def format_size(self, size):
        """Format file size to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def log_message(self, message, level="info"):
        """Add message to log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] ", level)
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def upload_folder(self):
        """Upload entire folder"""
        folder = filedialog.askdirectory(title="Select folder to upload")
        if folder:
            self._upload_folder(folder, os.path.basename(folder))

    def _upload_folder(self, local_path, remote_name):
        """Upload folder recursively"""
        if not self.connected:
            return
        
        try:
            # Create remote folder
            try:
                self.ftp.mkd(remote_name)
            except:
                pass
            
            # Save current path
            original_remote = self.current_remote_path
            
            # Enter remote folder
            self.ftp.cwd(remote_name)
            
            # Upload contents
            for item in os.listdir(local_path):
                item_path = os.path.join(local_path, item)
                if os.path.isfile(item_path):
                    self._upload_single_file(item_path)
                elif os.path.isdir(item_path):
                    self._upload_folder(item_path, item)
            
            # Return to original path
            self.ftp.cwd(original_remote)
            
        except Exception as e:
            self.log_message(f"Folder upload error: {e}", "error")

    # ==================== DIALOGS ====================
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
{self.APP_NAME} v{self.VERSION}

A professional FTP client built with Python.

Features:
• FTP and FTPS (TLS/SSL) support
• Upload and download files/folders
• Save multiple connections
• Passive/Active mode support
• Progress tracking
• Transfer logging

License: MIT

© 2024 HyperFTP Team
        """
        messagebox.showinfo("About", about_text.strip())

    def show_docs(self):
        """Show documentation"""
        docs = """
HyperFTP - Quick Start Guide

1. CONNECTION:
   - Enter host, port, username, and password
   - Check "Anonymous" for anonymous login
   - Check "TLS/SSL" for secure connections
   - Click "Connect"

2. FILE TRANSFER:
   - Double-click folders to navigate
   - Select files and click Upload/Download
   - Use right-click menu for more options

3. KEYBOARD SHORTCUTS:
   - Ctrl+N: New connection
   - Ctrl+U: Upload selected
   - Ctrl+D: Download selected
   - F5: Refresh local
   - F6: Refresh remote

4. SAVE CONNECTIONS:
   - Click "Save Connection" to save current settings
   - Select from dropdown to load saved connections
        """
        
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("500x400")
        
        text = scrolledtext.ScrolledText(doc_window, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert('1.0', docs.strip())
        text.config(state=tk.DISABLED)

    def on_closing(self):
        """Handle window close"""
        if self.connected:
            if messagebox.askyesno("Confirm Exit", "Disconnect and exit?"):
                self.disconnect_ftp()
                self.root.destroy()
        else:
            self.root.destroy()


# ==================== MAIN ====================

def main():
    """Application entry point"""
    root = tk.Tk()
    
    # Set icon (optional)
    try:
        root.iconbitmap('ftp_icon.ico')
    except:
        pass
    
    # Center window
    root.update_idletasks()
    width = 1000
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = HyperFTP(root)
    root.mainloop()


if __name__ == "__main__":
    main()