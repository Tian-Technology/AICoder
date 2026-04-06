#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import json
import os
import threading
import requests
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import sv_ttk
from tkhtmlview import HTMLScrolledText
import markdown
import sys
import shutil
import tempfile
import subprocess

def resource_path(relative_path):
    """获取资源的绝对路径（用于只读资源，如默认图标等）"""
    try:
        # PyInstaller 会将资源解压到 _MEIPASS 临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 非打包模式，返回脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def data_path(relative_path):
    """获取用户数据文件的路径（需要持久化，放在 exe 所在目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe 路径
        base_path = os.path.dirname(sys.executable)
    else:
        # 非打包模式，返回脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from model import (
    ALL_MODELS,
    get_model_display_name,
    get_model_provider,
    get_model_max_tokens,
    get_default_base_url_for_model
)

class AICoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AICoder - 智能对话助手")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        # 设置窗口图标
        icon_path = resource_path("aicoder.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        # 默认最大化窗口
        self.root.state('zoomed')
        
        # 设置主题颜色
        self.bg_color = "#f0f0f0"
        self.nav_color = "#2c3e50"
        self.text_color = "#333333"
        self.button_color = "#3498db"
        
        # 配置样式
        self.setup_styles()
        
        # 初始化数据（日志容器须先于 load_config，以便加载失败时可写日志）
        self.config_file = Path(data_path("config.json"))
        self.message_data_dir = Path(data_path("message_data"))
        self.logs = []
        self._log_scrolled = None
        self._max_log_entries = 4000
        
        # 创建message_data文件夹
        self.message_data_dir.mkdir(exist_ok=True)
        
        self.log("应用启动，开始初始化...", "INFO")
        self.load_config()
        
        # 初始化对话相关变量
        self.current_conversation_id = None
        self.conversations = {}  # 存储所有对话信息
        self.chat_history = []  # 当前对话的消息
        self.load_conversations()

        # 应用保存的主题
        theme = "dark" if self.config.get('dark_mode') else "light"
        self.log(f"应用主题: {theme}", "INFO")
        sv_ttk.set_theme(theme)

        # 初始化模型变量
        self.model_var = tk.StringVar(value=self.config.get('model', 'deepseek-r1'))
        self.log(f"初始化模型: {self.model_var.get()}", "INFO")
        
        # 初始化停止生成标志
        self._stop_generation = False

        # 创建界面
        self.log("开始创建界面组件...", "INFO")
        self.create_widgets()

        self._log_config_loaded()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.log("窗口关闭事件已绑定", "INFO")
        
        # 检查是否需要自动更新（仅在打包后执行）
        if getattr(sys, 'frozen', False):
            self.log("检测到打包环境，启动更新检查线程", "INFO")
            threading.Thread(target=self.check_for_updates, daemon=True).start()
        else:
            self.log("开发环境，跳过自动更新检查", "INFO")

    def on_closing(self):
        """用户点击关闭窗口时确认后退出"""
        if messagebox.askokcancel("退出", "确定要退出 AICoder 吗？"):
            self.log("用户确认退出应用", "INFO")
            self.root.destroy()

    def setup_styles(self):
        """设置 ttk 样式"""
        # 定义颜色样式
        self._refresh_custom_styles()
    
    def _refresh_custom_styles(self):
        """根据当前主题刷新自定义样式"""
        style = ttk.Style()
        # 根据当前主题微调颜色
        if sv_ttk.get_theme() == "dark":
            style.configure("Green.TLabel", foreground="#4caf50")
            style.configure("Orange.TLabel", foreground="#ff9800")
            style.configure("Red.TLabel", foreground="#f44336")
        else:
            style.configure("Green.TLabel", foreground="green")
            style.configure("Orange.TLabel", foreground="orange")
            style.configure("Red.TLabel", foreground="red")

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 1. 导航栏
        self.create_navigation(main_container)
        
        # 2. 主内容区域
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 默认显示主聊天界面
        self.show_chat()

    def create_navigation(self, parent):
        """创建导航栏"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Logo/标题
        logo_label = ttk.Label(nav_frame, text="AICoder", 
                             font=("微软雅黑", 16, "bold"), 
                             padding=20)
        logo_label.pack(side=tk.LEFT)
        
        # 导航按钮
        buttons_frame = ttk.Frame(nav_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=20)
        
        # 返回主页面按钮
        home_btn = ttk.Button(buttons_frame, text="🏠 主页", 
                            command=self.show_chat)
        home_btn.pack(side=tk.LEFT, padx=5)
        
        # 设置按钮
        settings_btn = ttk.Button(buttons_frame, text="⚙️ 设置", 
                                command=self.show_settings)
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空对话按钮
        clear_btn = ttk.Button(buttons_frame, text="🗑️ 清空", 
                             command=self.clear_chat)
        clear_btn.pack(side=tk.LEFT, padx=5)
        

        
        # 日志按钮
        log_btn = ttk.Button(buttons_frame, text="📋 日志", 
                           style="Nav.TButton", 
                           command=self.show_log)
        log_btn.pack(side=tk.LEFT, padx=5)
        
        # 更新按钮
        update_btn = ttk.Button(buttons_frame, text="🔄 更新", 
                           style="Nav.TButton", 
                           command=self.show_update)
        update_btn.pack(side=tk.LEFT, padx=5)
        
        # 关于按钮
        about_btn = ttk.Button(buttons_frame, text="ℹ️ 关于", 
                           style="Nav.TButton", 
                           command=self.show_about)
        about_btn.pack(side=tk.LEFT, padx=5)

    def show_welcome(self):
        """显示欢迎界面"""
        self.clear_content()
        
        welcome_frame = ttk.Frame(self.content_frame, style="Content.TFrame")
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 欢迎标题
        title_label = ttk.Label(welcome_frame, text="欢迎使用 AICoder", 
                              font=("微软雅黑", 24, "bold"))
        title_label.pack(pady=20)
        
        # 功能介绍
        intro_text = """
        AICoder 是一个强大的 AI 对话工具，支持多种模型：
        
        • DeepSeek-R1 - 深度求索推理模型
        • DeepSeek-V3.2 - 深度求索最新版本
        • GPT-4o - OpenAI 最新模型
        • 以及其他更多模型
        
        请先在右上角的"设置"中配置您的 API 密钥。
        """
        
        intro_label = ttk.Label(welcome_frame, text=intro_text, 
                              font=("微软雅黑", 12), 
                              justify=tk.LEFT)
        intro_label.pack(pady=10, anchor=tk.W)
        
        # 快速开始按钮
        quick_btn = ttk.Button(welcome_frame, text="🚀 快速开始", 
                             command=self.show_chat)
        quick_btn.pack(pady=20)

    def show_settings(self):
        """显示设置界面"""
        start_time = time.time()
        self.log("切换到设置界面", "INFO")
        self.clear_content()
        
        # 创建滚动容器
        canvas = tk.Canvas(self.content_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        
        # 创建设置框架
        settings_frame = ttk.Frame(canvas, style="Content.TFrame")
        # 确保设置框架能够自适应画布宽度
        window_id = canvas.create_window((0, 0), window=settings_frame, anchor="nw", width=self.content_frame.winfo_width())
        
        # 配置滚动区域
        def configure_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        settings_frame.bind("<Configure>", configure_scrollregion)
        
        # 监听画布大小变化，确保设置框架宽度始终与画布一致
        def on_canvas_resize(event):
            canvas.itemconfigure(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)
        
        # 绑定鼠标滚轮事件，让设置页面任意位置都可以用滚轮滑动
        def on_mouse_wheel(event):
            try:
                # 检查canvas是否仍然存在
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                # 如果canvas已被销毁，移除事件绑定
                self.root.unbind_all("<MouseWheel>")
                self.log(f"移除鼠标滚轮事件绑定: {e}", "DEBUG")
        self.root.bind_all("<MouseWheel>", on_mouse_wheel)
        
        # 标题
        title_label = ttk.Label(settings_frame, text="⚙️ 设置", 
                              font=('微软雅黑', 18, 'bold'))
        title_label.pack(pady=20)
        
        # 创建内容容器，撑满整个宽度
        content_container = ttk.Frame(settings_frame)
        content_container.pack(fill=tk.X, padx=20)
        
        # 模型选择
        model_frame = ttk.LabelFrame(content_container, text="选择模型", padding=15)
        model_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(model_frame, text="搜索并选择您要使用的 AI 模型：", 
                font=('微软雅黑', 10)).pack(pady=(0, 10))
        
        # 创建模型搜索和选择框架
        model_select_frame = ttk.Frame(model_frame)
        model_select_frame.pack(fill=tk.X, pady=5)
        
        # 搜索框
        search_frame = ttk.Frame(model_select_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索模型：", font=('微软雅黑', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_search_var = tk.StringVar()
        self.model_search_entry = ttk.Entry(search_frame, textvariable=self.model_search_var)
        self.model_search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        search_btn = ttk.Button(search_frame, text="🔍 搜索", command=self.search_models)
        search_btn.pack(side=tk.LEFT)
        
        # 模型列表 - 使用 ttk.Treeview
        self.model_listbox = ttk.Treeview(model_select_frame, height=10, columns=('model'), show='tree')
        # 不固定列宽，让其自适应宽度
        self.model_listbox.pack(fill=tk.X, pady=(0, 10))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(model_select_frame, orient="vertical", command=self.model_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.model_listbox.config(yscrollcommand=scrollbar.set)
        
        # 为模型列表添加鼠标滚轮事件，当鼠标在模型列表上时，滚动模型列表而不是整个页面
        def on_model_list_scroll(event):
            # 计算滚动单位
            delta = int(-1*(event.delta/120))
            # 滚动模型列表
            self.model_listbox.yview_scroll(delta, "units")
            # 阻止事件冒泡，避免触发页面滚动
            return "break"
        self.model_listbox.bind("<MouseWheel>", on_model_list_scroll)
        
        # 当前选择的模型
        self.model_var = tk.StringVar(value=self.config.get('model', 'deepseek-r1'))
        self.selected_model_label = ttk.Label(model_select_frame, text=f"当前选择: {get_model_display_name(self.config.get('model', 'deepseek-r1'))}", 
                                           font=('微软雅黑', 9))
        self.selected_model_label.pack(pady=(0, 5))
        
        # 选定按钮
        select_btn = ttk.Button(model_select_frame, text="✅ 选定模型", command=self.confirm_model_selection)
        select_btn.pack(pady=(5, 10))
        
        # 绑定选择事件
        self.model_listbox.bind('<<ListboxSelect>>', self.on_model_select)
        
        # 初始化模型列表
        self.log("初始化模型列表", "INFO")
        self.populate_model_list()
        
        # 绑定回车键搜索
        self.model_search_entry.bind('<Return>', lambda event: self.search_models())
        
        # 绑定搜索框内容变化事件
        self.model_search_var.trace_add('write', self.on_search_change)
        
        # API 密钥设置
        api_frame = ttk.LabelFrame(content_container, text="API 密钥配置", padding=15)
        api_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(api_frame, text="请输入您的 API 密钥：", 
                font=('微软雅黑', 10)).pack(pady=5)
        
        self.api_key_entry = ttk.Entry(api_frame, show="*")
        self.api_key_entry.insert(0, self.config.get('api_key', ''))
        self.api_key_entry.pack(fill=tk.X, pady=5)
        
        # 显示/隐藏密钥
        self.show_key_var = tk.BooleanVar()
        ttk.Checkbutton(api_frame, text="显示密钥", variable=self.show_key_var,
                      command=self.toggle_api_key_visibility).pack(pady=5)
        
        # API 完整地址：留空时按上方所选模型自动使用常见服务商端点（DeepSeek / OpenAI / 智谱 / 通义 / Moonshot）
        ttk.Label(
            api_frame,
            text="API 地址（chat completions 完整 URL，可留空以根据模型自动选择）：",
            font=('微软雅黑', 10),
            wraplength=1000,  # 增加换行长度，适应宽屏幕
            justify=tk.LEFT,
        ).pack(pady=5)
        
        self.base_url_entry = ttk.Entry(api_frame)
        self.base_url_entry.insert(0, self.config.get('base_url', ''))
        self.base_url_entry.pack(fill=tk.X, pady=5)
        
        # 主题切换
        theme_frame = ttk.LabelFrame(content_container, text="主题设置", padding=15)
        theme_frame.pack(fill=tk.X, pady=10)
        
        self.dark_mode_var = tk.BooleanVar(value=self.config.get('dark_mode', False))
        def toggle_theme():
            if self.dark_mode_var.get():
                sv_ttk.set_theme("dark")
                self.config['dark_mode'] = True
                self.log("切换到深色模式", "INFO")
            else:
                sv_ttk.set_theme("light")
                self.config['dark_mode'] = False
                self.log("切换到浅色模式", "INFO")
            self.save_config()
            # 刷新自定义样式
            self._refresh_custom_styles()
        
        ttk.Checkbutton(theme_frame, text="深色模式", variable=self.dark_mode_var, 
                       command=toggle_theme).pack(pady=5)
        

        
        # 保存按钮
        save_btn = ttk.Button(content_container, text="💾 保存设置", 
                            command=self.save_settings)
        save_btn.pack(pady=20)
        elapsed = time.time() - start_time
        self.log(f"设置界面加载完成 | 耗时: {elapsed:.2f}s", "INFO")

    def populate_model_list(self):
        """填充模型列表"""
        self.all_models = ALL_MODELS
        
        # 清空列表并添加所有模型
        for item in self.model_listbox.get_children():
            self.model_listbox.delete(item)
        
        for model_id, display_name in self.all_models:
            self.model_listbox.insert('', 'end', text=f"{display_name} ({model_id})", values=(model_id,))
        
        # 设置当前选择
        current_model = self.config.get('model', 'deepseek-r1')
        self.update_selected_model_label(current_model)

    def search_models(self):
        """搜索模型"""
        search_text = self.model_search_var.get().strip().lower()
        if not search_text:
            self.populate_model_list()
            return
        
        # 清空列表
        for item in self.model_listbox.get_children():
            self.model_listbox.delete(item)
        
        # 搜索匹配的模型
        found_models = []
        for model_id, display_name in self.all_models:
            if (search_text in model_id.lower() or 
                search_text in display_name.lower() or
                search_text in get_model_provider(model_id).lower()):
                found_models.append((model_id, display_name))
        
        # 添加到列表
        for model_id, display_name in found_models:
            self.model_listbox.insert('', 'end', text=f"{display_name} ({model_id})", values=(model_id,))
        
        if not found_models:
            self.model_listbox.insert('', 'end', text="未找到匹配的模型", values=('none',))

    def on_search_change(self, *args):
        """搜索框内容变化时的处理"""
        # 延迟搜索，避免频繁触发
        if hasattr(self, '_search_after_id'):
            self.root.after_cancel(self._search_after_id)
        self._search_after_id = self.root.after(300, self.search_models)

    def on_model_select(self, event):
        """模型选择事件"""
        selection = self.model_listbox.selection()
        if selection:
            item = selection[0]
            model_id = self.model_listbox.item(item, 'values')[0]
            if model_id and model_id != 'none':
                self.model_var.set(model_id)
                self.update_selected_model_label(model_id)
    
    def confirm_model_selection(self):
        """确认模型选择"""
        selection = self.model_listbox.selection()
        if not selection:
            messagebox.showinfo("提示", "请先从列表中选择一个模型")
            return
        
        item = selection[0]
        model_id = self.model_listbox.item(item, 'values')[0]
        if model_id and model_id != 'none':
            self.model_var.set(model_id)
            self.update_selected_model_label(model_id)
            messagebox.showinfo("成功", f"已选定模型: {get_model_display_name(model_id)}")
            self.log(f"选定模型: {model_id} ({get_model_display_name(model_id)})", "INFO")

            # 更新主页显示的模型信息
            self.show_chat()

    def update_selected_model_label(self, model_id):
        """更新当前选择的模型标签"""
        display_name = get_model_display_name(model_id)
        self.selected_model_label.config(text=f"当前选择: {display_name}")

    def update_conversation_list(self):
        """更新对话列表"""
        try:
            if hasattr(self, 'conversation_listbox') and self.conversation_listbox.winfo_exists():
                # 清空列表
                for item in self.conversation_listbox.get_children():
                    self.conversation_listbox.delete(item)
                
                # 添加对话
                for conversation_id, info in self.conversations.items():
                    # 格式化更新时间
                    updated_at = info.get('updated_at', '')
                    if updated_at:
                        try:
                            dt = datetime.fromisoformat(updated_at)
                            updated_at = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            updated_at = updated_at[:16]
                    
                    # 添加到列表
                    self.conversation_listbox.insert('', 'end', iid=conversation_id, 
                                                  text=info['name'],
                                                  values=(updated_at,))
                
                # 选中当前对话
                if self.current_conversation_id:
                    self.conversation_listbox.selection_set(self.current_conversation_id)
        except Exception as e:
            self.log(f"更新对话列表失败: {e}", "ERROR")
    
    def show_chat(self):
        """显示对话界面"""
        start_time = time.time()
        self.log("切换到对话界面", "INFO")
        self.clear_content()
        
        # 检查配置
        if not self.check_config():
            self.log("配置不完整，跳转到设置界面", "WARNING")
            messagebox.showwarning("警告", "请先在设置中配置 API 密钥！")
            self.show_settings()
            return
        
        # 创建主容器，分为左侧对话栏和右侧聊天区域
        main_container = ttk.Frame(self.content_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 左侧对话栏
        conversation_frame = ttk.LabelFrame(main_container, text="对话", width=250)
        conversation_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 对话列表
        conversation_list_frame = ttk.Frame(conversation_frame)
        conversation_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树状视图作为对话列表
        self.conversation_listbox = ttk.Treeview(conversation_list_frame, 
                                               columns=('updated_at'), 
                                               show='tree')
        self.conversation_listbox.heading('#0', text='对话名称')
        self.conversation_listbox.heading('updated_at', text='更新时间')
        self.conversation_listbox.column('updated_at', width=100)
        
        # 添加滚动条
        conversation_scrollbar = ttk.Scrollbar(conversation_list_frame, 
                                             orient="vertical", 
                                             command=self.conversation_listbox.yview)
        conversation_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.conversation_listbox.config(yscrollcommand=conversation_scrollbar.set)
        
        self.conversation_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 对话操作按钮
        button_frame = ttk.Frame(conversation_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 新对话按钮
        new_conversation_btn = ttk.Button(button_frame, text="➕ 新对话", 
                                        command=self.create_new_conversation)
        new_conversation_btn.pack(fill=tk.X, pady=(0, 5))
        
        # 删除对话按钮
        delete_conversation_btn = ttk.Button(button_frame, text="🗑️ 删除对话", 
                                           command=self._on_delete_conversation)
        delete_conversation_btn.pack(fill=tk.X, pady=(0, 5))
        
        # 重命名对话按钮
        rename_conversation_btn = ttk.Button(button_frame, text="✏️ 重命名对话", 
                                           command=self._on_rename_conversation)
        rename_conversation_btn.pack(fill=tk.X)
        
        # 右侧聊天区域
        chat_container = ttk.Frame(main_container)
        chat_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建滚动容器
        canvas = tk.Canvas(chat_container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        
        # 创建聊天容器
        chat_frame = ttk.Frame(canvas, style="Content.TFrame")
        # 使用 width 参数确保聊天容器占满整个画布
        window_id = canvas.create_window((0, 0), window=chat_frame, anchor="nw", width=chat_container.winfo_width())
        
        # 配置滚动区域
        def configure_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 动态调整聊天容器宽度
            canvas.itemconfigure(window_id, width=canvas.winfo_width())
        chat_frame.bind("<Configure>", configure_scrollregion)
        
        # 监听画布大小变化
        def on_canvas_resize(event):
            canvas.itemconfigure(window_id, width=event.width)
        canvas.bind("<Configure>", on_canvas_resize)
        
        # 绑定鼠标滚轮事件
        def on_mouse_wheel(event):
            try:
                # 检查canvas是否仍然存在
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                # 如果canvas已被销毁，移除事件绑定
                self.root.unbind_all("<MouseWheel>")
                self.log(f"移除鼠标滚轮事件绑定: {e}", "DEBUG")
        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        # 绑定对话列表选择事件
        def on_conversation_select(event):
            selection = self.conversation_listbox.selection()
            if selection:
                conversation_id = selection[0]
                if conversation_id != self.current_conversation_id:
                    self.switch_conversation(conversation_id)
        
        self.conversation_listbox.bind('<<TreeviewSelect>>', on_conversation_select)
        
        # 更新对话列表
        self.update_conversation_list()
        
        # 上下文窗口信息
        self.context_frame = ttk.Frame(chat_frame)
        self.context_frame.pack(fill=tk.X, pady=(0, 5), padx=10)
        
        used_tokens = self.calculate_used_tokens()
        model = self.model_var.get()
        max_tokens = get_model_max_tokens(model)
        remaining_tokens = max_tokens - used_tokens
        
        context_info = f"上下文窗口: 已使用 {used_tokens} / {max_tokens} tokens (剩余 {remaining_tokens} tokens)"
        # 根据剩余token数设置初始样式
        if remaining_tokens < 0:
            style = "Red.TLabel"
        elif remaining_tokens < max_tokens * 0.2:
            style = "Orange.TLabel"
        else:
            style = "Green.TLabel"
        self.context_label = ttk.Label(self.context_frame, text=context_info, 
                               font=("微软雅黑", 9),
                               style=style)
        self.context_label.pack(pady=5, anchor=tk.W)
        
        # API 用量显示
        self.usage_label = ttk.Label(self.context_frame, 
                                   font=("微软雅黑", 9))
        self.usage_label.pack(pady=5, anchor=tk.W)
        self.update_usage_display()
        
        # 显示当前模型信息
        model_info = f"当前模型: {self.get_model_name()}"
        model_label = ttk.Label(self.context_frame, text=model_info, 
                              font=('微软雅黑', 9))
        model_label.pack(pady=5, anchor=tk.W)
        
        # 根据当前主题设置合适的背景和前景色
        if sv_ttk.get_theme() == "dark":
            bg_color = "#2d2d2d"
            fg_color = "#e0e0e0"
        else:
            bg_color = "#ffffff"
            fg_color = "#333333"
        
        # 对话历史区域
        history_frame = ttk.LabelFrame(chat_frame, text="对话历史", padding=5)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=10)
        
        # 搜索框区域（放在历史记录上方）
        search_frame = ttk.Frame(history_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索对话:", font=('微软雅黑', 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        search_btn = ttk.Button(search_frame, text="🔍 搜索", command=self.search_chat)
        search_btn.pack(side=tk.LEFT)
        
        clear_search_btn = ttk.Button(search_frame, text="🗑️ 清除", command=self.clear_search)
        clear_search_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # 创建滚动条
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 使用 tk.Text 来显示文本内容
        self.chat_display = tk.Text(history_frame, 
                                   height=15,
                                   font=('微软雅黑', 10),
                                   wrap=tk.WORD,
                                   padx=10,
                                   pady=10,
                                   yscrollcommand=history_scrollbar.set)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        history_scrollbar.config(command=self.chat_display.yview)
        
        # 配置标签用于高亮显示
        self.chat_display.tag_config("highlight", background="yellow", foreground="black")
        self.chat_display.tag_config("user", foreground="green", font=('微软雅黑', 10, 'bold'))
        self.chat_display.tag_config("ai", foreground="blue", font=('微软雅黑', 10, 'bold'))
        self.chat_display.tag_config("system", foreground="red", font=('微软雅黑', 10, 'bold'))
        
        # 输入区域（放在底部）
        input_frame = ttk.LabelFrame(chat_frame, text="输入消息", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(input_frame, 
                                                   height=8,
                                                   font=('微软雅黑', 10),
                                                   bg=bg_color,
                                                   fg=fg_color)
        self.input_text.pack(fill=tk.X, pady=(0, 10))
        # 绑定回车键发送消息
        self.input_text.bind('<Return>', lambda event: self.send_message())
        # 绑定 Shift+回车键换行
        self.input_text.bind('<Shift-Return>', lambda event: self.input_text.insert(tk.INSERT, '\n'))
        
        # 按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)
        
        send_btn = ttk.Button(button_frame, text="📤 发送", 
                            style="Action.TButton",
                            command=self.send_message)
        send_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.send_button = send_btn
        
        # 停止生成按钮
        stop_btn = ttk.Button(button_frame, text="⏹️ 停止生成", 
                             style="Action.TButton",
                             command=self.stop_generation,
                             state=tk.DISABLED)
        stop_btn.pack(side=tk.LEFT, padx=5)
        self.stop_button = stop_btn
        
        clear_input_btn = ttk.Button(button_frame, text="🗑️ 清空输入", 
                                   style="Action.TButton",
                                   command=self.clear_input)
        clear_input_btn.pack(side=tk.LEFT, padx=5)
        
        upload_btn = ttk.Button(button_frame, text="📁 上传文件", 
                               style="Action.TButton",
                               command=self.upload_file)
        upload_btn.pack(side=tk.LEFT, padx=5)
        
        # 显示聊天历史
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        
        if self.chat_history:
            self.log(f"显示 {len(self.chat_history)} 条聊天记录", "INFO")
            for timestamp, sender, message in self.chat_history:
                if sender == "AI":
                    self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "ai")
                    self.chat_display.insert(tk.END, f"{message}\n\n")
                elif sender == "用户":
                    self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "user")
                    self.chat_display.insert(tk.END, f"{message}\n\n")
                else:
                    self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "system")
                    self.chat_display.insert(tk.END, f"{message}\n\n")
        else:
            # 显示欢迎信息
            self.log("显示欢迎信息", "INFO")
            welcome_message = "欢迎使用 AICoder\n"
            welcome_message += "这是一个智能对话助手，可以帮助您解答问题、编写代码、生成内容等。\n"
            welcome_message += "请在下方输入框中输入您的问题，然后按回车键发送。\n"
            self.chat_display.insert(tk.END, welcome_message)
        
        self.chat_display.config(state=tk.DISABLED)
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        
        # 更新上下文窗口信息
        self.update_context_info()
        elapsed = time.time() - start_time
        self.log(f"对话界面加载完成 | 耗时: {elapsed:.2f}s", "INFO")


    
    def show_update(self):
        """显示更新页面"""
        self.log("切换到更新页面", "INFO")
        self.clear_content()
        
        update_frame = ttk.Frame(self.content_frame)
        update_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(update_frame, text="🔄 更新", 
                              font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=20)
        
        # 创建滚动容器
        canvas = tk.Canvas(update_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(update_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        
        # 创建内容框架
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # 版本信息
        version_frame = ttk.LabelFrame(content_frame, text="版本信息", padding=15)
        version_frame.pack(fill=tk.X, pady=10)
        
        # 读取本地版本
        version_file = Path(data_path("version.txt"))
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                local_version = f.read().strip()
        else:
            # 默认版本
            local_version = "v1.0.0"
            with open(version_file, 'w', encoding='utf-8') as f:
                f.write(local_version)
        
        ttk.Label(version_frame, text=f"当前版本: {local_version}", 
                 font=("微软雅黑", 12)).pack(pady=5, anchor=tk.W)
        
        # 最新版本信息（初始为未知）
        self.latest_version_var = tk.StringVar(value="未知")
        ttk.Label(version_frame, text="最新版本: ", 
                 font=("微软雅黑", 12)).pack(side=tk.LEFT, pady=5)
        ttk.Label(version_frame, textvariable=self.latest_version_var, 
                 font=("微软雅黑", 12, "bold")).pack(side=tk.LEFT, pady=5)
        
        # 更新内容
        update_content_frame = ttk.LabelFrame(content_frame, text="更新内容", padding=15)
        update_content_frame.pack(fill=tk.X, pady=10)
        
        self.update_content_var = tk.StringVar(value="请点击检查更新按钮获取最新更新信息")
        update_content_label = ttk.Label(update_content_frame, textvariable=self.update_content_var, 
                                        font=("微软雅黑", 10), justify=tk.LEFT, wraplength=800)
        update_content_label.pack(pady=5, anchor=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 检查更新按钮
        check_update_btn = ttk.Button(button_frame, text="🔍 检查更新", 
                                   command=self.check_for_updates)
        check_update_btn.pack(side=tk.LEFT, padx=5)
        
        # 快速开始按钮
        quick_btn = ttk.Button(button_frame, text="🚀 开始使用", 
                             command=self.show_chat)
        quick_btn.pack(side=tk.LEFT, padx=5)
        
        # 绑定滚动事件
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", on_configure)
        
        # 绑定鼠标滚轮事件
        def on_mouse_wheel(event):
            try:
                # 检查canvas是否仍然存在
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                # 如果canvas已被销毁，移除事件绑定
                self.root.unbind_all("<MouseWheel>")
                self.log(f"移除鼠标滚轮事件绑定: {e}", "DEBUG")
        
        # 绑定鼠标滚轮事件到整个窗口
        self.root.bind_all("<MouseWheel>", on_mouse_wheel)
        
        self.log("更新页面加载完成", "INFO")
    
    def show_about(self):
        """显示关于页面"""
        self.log("切换到关于页面", "INFO")
        self.clear_content()
        
        about_frame = ttk.Frame(self.content_frame)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(about_frame, text="ℹ️ 关于 AICoder", 
                              font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=20)
        
        # 创建滚动容器
        canvas = tk.Canvas(about_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(about_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        
        # 创建内容框架
        content_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)
        
        # 软件介绍
        intro_text = """
        AICoder 是一款功能强大的智能对话助手，专为各大 AI 程序测试员服务，旨在帮助用户更高效地与 AI 进行交互和测试。
        
        主要功能：
        • 支持多种 AI 模型，包括 OpenAI、DeepSeek、Google Gemini、Anthropic Claude 等
        • 实时 API 用量统计，防止不知不觉用超
        • 支持 Markdown 格式显示，包括数学公式处理
        • 文件上传功能，方便分享代码和文档
        • 按回车键发送消息，提高输入效率
        • 多对话管理，支持创建、删除和重命名对话
        • 窗口默认最大化，提供更大的工作区域
        • 友好的用户界面，易于操作
        
        为 AI 测试员量身定制：
        • 多模型切换：快速在不同 AI 模型间切换，比较不同模型的表现
        • 详细日志记录：记录所有 API 调用和响应，便于测试分析
        • 对话隔离：每个测试场景可以创建独立对话，避免上下文干扰
        • 灵活配置：支持自定义 API 端点和参数，满足不同测试需求
        • 批量测试：可以快速创建多个对话进行并行测试
        
        设计理念：
        • 简洁易用：提供直观的用户界面，让用户专注于与 AI 的交互
        • 功能强大：集成多种 AI 模型，满足不同场景的需求
        • 高效便捷：支持快捷键和文件上传等功能，提高工作效率
        • 透明可控：实时显示 API 用量，让用户对使用情况一目了然
        • 专业可靠：为 AI 测试员提供稳定、高效的测试环境
        
        技术架构：
        • 前端：基于 Tkinter 的图形界面
        • 后端：Python 实现，支持多种 AI API
        • 配置管理：本地 JSON 配置文件
        • 日志系统：详细的运行日志记录
        • 对话存储：每个对话独立存储，便于管理和分析
        
        使用提示：
        • 在设置中配置 API 密钥和选择模型
        • 使用文件上传功能分享代码和文档
        • 按回车键发送消息，Shift+回车键换行
        • 查看 API 用量统计，合理控制使用
        • 为不同测试场景创建独立对话
        • 利用详细日志进行测试分析
        
        未来规划：
        • 支持更多 AI 模型和服务商
        • 实现对话历史的云端同步
        • 添加测试报告生成功能
        • 支持批量测试和自动化测试
        • 优化用户界面和交互体验
        • 支持多语言界面
        
        版本：1.0.0
        开发者：AICoder Team By Tian-Technology
        版权所有 © 2026 Tian-Technology
        
        联系方式：
        • 邮箱：tiantechnology@163.com
        • 网站：http://tiantech.zjjsw.com
        • GitHub：https://github.com/Tian-Technology/
        """
        
        intro_label = ttk.Label(content_frame, text=intro_text, 
                              font=("微软雅黑", 12), 
                              justify=tk.LEFT)
        intro_label.pack(pady=10, anchor=tk.W)
        
        # 快速开始按钮
        quick_btn = ttk.Button(content_frame, text="🚀 开始使用", 
                             command=self.show_chat)
        quick_btn.pack(pady=20)
        
        # 绑定滚动事件
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", on_configure)
        
        # 绑定鼠标滚轮事件
        def on_mouse_wheel(event):
            try:
                # 检查canvas是否仍然存在
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                # 如果canvas已被销毁，移除事件绑定
                self.root.unbind_all("<MouseWheel>")
                self.log(f"移除鼠标滚轮事件绑定: {e}", "DEBUG")
        
        # 绑定鼠标滚轮事件到整个窗口
        self.root.bind_all("<MouseWheel>", on_mouse_wheel)
        
        self.log("关于页面加载完成", "INFO")
    
    def show_log(self):
        """显示日志页面"""
        self.log("切换到日志页面", "INFO")
        self.clear_content()
        
        log_frame = ttk.Frame(self.content_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(log_frame, text="📋 日志", 
                              font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=10)
        
        # 日志显示区域，根据主题设置颜色
        if sv_ttk.get_theme() == "dark":
            log_bg = "#2d2d2d"
            log_fg = "#e0e0e0"
        else:
            log_bg = "#ffffff"
            log_fg = "#333333"
        
        log_display = scrolledtext.ScrolledText(log_frame, 
                                               width=80, height=25,
                                               font=("微软雅黑", 10),
                                               state=tk.DISABLED,
                                               bg=log_bg,
                                               fg=log_fg)
        log_display.pack(fill=tk.BOTH, expand=True, pady=10)
        self._log_scrolled = log_display

        # 显示日志内容
        log_display.config(state=tk.NORMAL)
        log_count = len(self.logs)
        if self.logs:
            # 先显示所有现有日志
            for log_entry in self.logs:
                log_display.insert(tk.END, f"{log_entry}\n")
            # 再记录显示日志的信息
            self.log(f"显示 {log_count} 条日志记录", "INFO")
        else:
            log_display.insert(tk.END, "暂无日志记录\n")
            self.log("显示无日志记录提示", "INFO")
        log_display.config(state=tk.DISABLED)
        
        # 按钮区域
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 清空日志按钮
        clear_log_btn = ttk.Button(button_frame, text="🗑️ 清空日志", 
                                 command=lambda: self.clear_log(log_display))
        clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存日志按钮
        save_log_btn = ttk.Button(button_frame, text="💾 保存日志", 
                                 command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=5)
        self.log("日志页面加载完成", "INFO")
    
    def clear_log(self, log_display):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空所有日志吗？"):
            self.logs = []
            log_display.config(state=tk.NORMAL)
            log_display.delete("1.0", tk.END)
            log_display.config(state=tk.DISABLED)
            self.log("运行日志已清空（以下为新的记录）", "INFO")
    
    def save_log(self):
        """保存日志"""
        if not self.logs:
            messagebox.showinfo("提示", "没有日志内容可保存")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="保存日志"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for log_entry in self.logs:
                        f.write(f"{log_entry}\n")
                self.log(f"日志已导出到文件: {filename}", "INFO")
                messagebox.showinfo("成功", "日志已保存！")
            except Exception as e:
                self.log(f"导出日志失败: {e}", "ERROR")
                messagebox.showerror("错误", f"保存失败: {e}")

    def clear_content(self):
        """清空内容区域"""
        self._log_scrolled = None
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def clear_chat(self):
        """清空对话历史与当前对话区内容"""
        if not messagebox.askyesno("确认", "确定要清空当前对话吗？"):
            return
        self.chat_history = []
        self.save_chat_history()  # 保存空记录
        self.log("已清空对话历史", "INFO")
        cd = getattr(self, "chat_display", None)
        if cd is not None:
            try:
                if cd.winfo_exists():
                    cd.config(state=tk.NORMAL)
                    cd.delete("1.0", tk.END)
                    # 显示欢迎信息
                    welcome_message = "欢迎使用 AICoder\n"
                    welcome_message += "这是一个智能对话助手，可以帮助您解答问题、编写代码、生成内容等。\n"
                    welcome_message += "请在下方输入框中输入您的问题，然后按回车键发送。\n"
                    cd.insert(tk.END, welcome_message)
                    cd.config(state=tk.DISABLED)
            except tk.TclError:
                pass
        if hasattr(self, "update_context_info"):
            self.update_context_info()

    def clear_input(self):
        """清空输入框"""
        it = getattr(self, "input_text", None)
        if it is not None:
            try:
                if it.winfo_exists():
                    it.delete("1.0", tk.END)
            except tk.TclError:
                pass
    
    def upload_file(self):
        """上传文件"""
        # 打开文件选择对话框
        filename = filedialog.askopenfilename(
            title="选择要上传的文件",
            filetypes=[("文本文件", "*.txt"), ("Python文件", "*.py"), ("所有文件", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # 读取文件内容
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 将文件内容添加到输入框
            self.input_text.insert(tk.END, f"[文件内容] {filename}\n\n{content}")
            self.log(f"已上传文件: {filename}", "INFO")
        except Exception as e:
            self.log(f"上传文件失败: {e}", "ERROR")
            messagebox.showerror("错误", f"上传文件失败: {e}")



    def toggle_api_key_visibility(self):
        """切换 API 密钥显示/隐藏"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def save_settings(self):
        """保存设置"""
        model = self.model_var.get()
        api_key = self.api_key_entry.get().strip()
        base_url = self.base_url_entry.get().strip()
        
        if not api_key:
            self.log("保存设置失败：API 密钥为空", "WARNING")
            messagebox.showwarning("警告", "请输入 API 密钥！")
            return
        
        old_model = self.config.get('model')
        old_base_url = self.config.get('base_url')
        
        self.config['model'] = model
        self.config['api_key'] = api_key
        self.config['base_url'] = base_url
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            ep = self._format_api_endpoint_for_log(base_url) if base_url else "留空(按模型自动推断)"
            changes = []
            if old_model != model:
                changes.append(f"模型: {old_model} → {model}")
            if old_base_url != base_url:
                changes.append(f"API 地址: {self._format_api_endpoint_for_log(old_base_url)} → {ep}")
            if changes:
                self.log(f"设置已保存 | {', '.join(changes)}", "INFO")
            else:
                self.log("设置已保存 | 无变更", "INFO")
            messagebox.showinfo("成功", "设置已保存！")
        except Exception as e:
            self.log(f"保存设置失败: {e}", "ERROR")
            messagebox.showerror("错误", f"保存设置失败: {e}")

    def load_config(self):
        """加载配置"""
        default_config = {
            "model": "deepseek-r1",
            "api_key": "",
            "base_url": "",
            "monthly_usage": 0,
            "current_month": datetime.now().strftime("%Y-%m"),
            "dark_mode": False
        }
        
        if self.config_file.exists():
            self.log(f"开始加载配置文件: {self.config_file}", "INFO")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # 合并默认配置，确保所有键都存在
                missing_keys = []
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
                        missing_keys.append(key)
                if missing_keys:
                    self.log(f"配置文件缺少键，已补充: {', '.join(missing_keys)}", "INFO")
                self.log(f"配置加载成功 | 模型: {self.config.get('model')} | 主题: {'深色' if self.config.get('dark_mode') else '浅色'}", "INFO")
            except Exception as e:
                self.config = default_config
                self.log(f"读取 config.json 失败: {e}，已使用默认配置", "WARNING")
        else:
            self.config = default_config
            self.log(f"未找到 config.json 文件: {self.config_file}，已使用默认配置", "INFO")
        
        # 检查是否需要重置月度用量
        self.check_and_reset_monthly_usage()

    def check_config(self):
        """检查配置是否完整"""
        return bool(self.config.get('api_key'))
    
    def check_and_reset_monthly_usage(self):
        """检查是否需要重置月度用量"""
        current_month = datetime.now().strftime("%Y-%m")
        if self.config.get('current_month') != current_month:
            self.config['current_month'] = current_month
            self.config['monthly_usage'] = 0
            self.save_config()
            self.log("月度用量已重置", "INFO")
    

    

    
    def update_api_usage(self, tokens):
        """更新 API 用量统计"""
        self.check_and_reset_monthly_usage()
        self.config['monthly_usage'] += tokens
        self.save_config()
        # 更新界面显示
        if hasattr(self, 'usage_label') and self.usage_label:
            self.update_usage_display()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.log(f"配置保存成功: {self.config_file}", "INFO")
        except Exception as e:
            self.log(f"保存配置失败: {e}", "ERROR")

    def create_new_conversation(self):
        """创建新对话"""
        try:
            # 生成唯一的对话ID
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            # 创建对话信息
            self.conversations[conversation_id] = {
                'name': f'新对话 {len(self.conversations) + 1}',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'messages': []
            }
            # 切换到新对话
            self.switch_conversation(conversation_id)
            # 保存对话
            self.save_conversation(conversation_id)
            # 更新对话列表
            if hasattr(self, 'conversation_listbox') and self.conversation_listbox.winfo_exists():
                self.update_conversation_list()
            self.log(f"创建新对话: {conversation_id}", "INFO")
            return conversation_id
        except Exception as e:
            self.log(f"创建新对话失败: {e}", "ERROR")
            return None
    
    def switch_conversation(self, conversation_id):
        """切换到指定对话"""
        try:
            if conversation_id in self.conversations:
                self.current_conversation_id = conversation_id
                self.chat_history = self.conversations[conversation_id]['messages']
                self.log(f"切换到对话: {self.conversations[conversation_id]['name']}", "INFO")
                # 如果当前在聊天界面，更新显示
                if hasattr(self, 'chat_display') and self.chat_display.winfo_exists():
                    self.show_chat()
                # 更新对话列表
                if hasattr(self, 'conversation_listbox') and self.conversation_listbox.winfo_exists():
                    self.update_conversation_list()
        except Exception as e:
            self.log(f"切换对话失败: {e}", "ERROR")
    
    def save_conversation(self, conversation_id=None):
        """保存对话到文件"""
        try:
            if conversation_id is None:
                conversation_id = self.current_conversation_id
            
            if conversation_id and conversation_id in self.conversations:
                # 更新对话信息
                self.conversations[conversation_id]['messages'] = self.chat_history
                self.conversations[conversation_id]['updated_at'] = datetime.now().isoformat()
                
                # 保存到文件
                file_path = self.message_data_dir / f"{conversation_id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.conversations[conversation_id], f, indent=2, ensure_ascii=False)
                self.log(f"保存对话: {self.conversations[conversation_id]['name']}", "INFO")
        except Exception as e:
            self.log(f"保存对话失败: {e}", "ERROR")
    
    def save_chat_history(self):
        """保存聊天记录到文件"""
        try:
            # 保存当前对话到独立文件
            self.save_conversation()
        except Exception as e:
            self.log(f"保存聊天记录失败: {e}", "ERROR")
    
    def delete_conversation(self, conversation_id):
        """删除对话"""
        try:
            if conversation_id in self.conversations:
                # 保存对话名称用于日志
                conversation_name = self.conversations[conversation_id]['name']
                
                # 删除文件
                file_path = self.message_data_dir / f"{conversation_id}.json"
                if file_path.exists():
                    file_path.unlink()
                
                # 从内存中删除
                del self.conversations[conversation_id]
                
                self.log(f"删除对话: {conversation_name}", "INFO")
                
                # 如果删除的是当前对话，切换到其他对话
                if self.current_conversation_id == conversation_id:
                    if self.conversations:
                        # 切换到第一个对话
                        first_conversation_id = next(iter(self.conversations.keys()))
                        self.switch_conversation(first_conversation_id)
                    else:
                        # 创建新对话
                        self.create_new_conversation()
                
                # 更新对话列表
                if hasattr(self, 'conversation_listbox') and self.conversation_listbox.winfo_exists():
                    self.update_conversation_list()
        except Exception as e:
            self.log(f"删除对话失败: {e}", "ERROR")
    
    def _on_delete_conversation(self):
        """处理删除对话的按钮点击事件"""
        try:
            selection = self.conversation_listbox.selection()
            if selection:
                conversation_id = selection[0]
                conversation_name = self.conversations[conversation_id]['name']
                
                # 确认删除
                if messagebox.askyesno("确认删除", f"确定要删除对话 '{conversation_name}' 吗？"):
                    self.delete_conversation(conversation_id)
        except Exception as e:
            self.log(f"删除对话操作失败: {e}", "ERROR")
    
    def _on_rename_conversation(self):
        """处理重命名对话的按钮点击事件"""
        try:
            selection = self.conversation_listbox.selection()
            if selection:
                conversation_id = selection[0]
                old_name = self.conversations[conversation_id]['name']
                
                # 输入新名称
                new_name = simpledialog.askstring("重命名对话", f"请输入对话的新名称:", 
                                               initialvalue=old_name)
                if new_name and new_name.strip():
                    self.rename_conversation(conversation_id, new_name.strip())
        except Exception as e:
            self.log(f"重命名对话操作失败: {e}", "ERROR")
    
    def rename_conversation(self, conversation_id, new_name):
        """重命名对话"""
        try:
            if conversation_id in self.conversations:
                old_name = self.conversations[conversation_id]['name']
                self.conversations[conversation_id]['name'] = new_name
                self.save_conversation(conversation_id)
                self.log(f"重命名对话: {old_name} → {new_name}", "INFO")
                
                # 更新对话列表
                if hasattr(self, 'conversation_listbox') and self.conversation_listbox.winfo_exists():
                    self.update_conversation_list()
        except Exception as e:
            self.log(f"重命名对话失败: {e}", "ERROR")

    def load_conversations(self):
        """加载所有对话"""
        try:
            # 遍历message_data文件夹中的所有json文件
            for file_path in self.message_data_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    conversation_id = file_path.stem
                    self.conversations[conversation_id] = {
                        'name': data.get('name', f'对话 {conversation_id}'),
                        'created_at': data.get('created_at'),
                        'updated_at': data.get('updated_at'),
                        'messages': data.get('messages', [])
                    }
                except Exception as e:
                    self.log(f"加载对话 {file_path.name} 失败: {e}", "WARNING")
            self.log(f"已加载 {len(self.conversations)} 个对话", "INFO")
            
            # 如果没有对话，创建一个默认对话
            if not self.conversations:
                self.create_new_conversation()
            else:
                # 选择第一个对话作为当前对话
                first_conversation_id = next(iter(self.conversations.keys()))
                self.switch_conversation(first_conversation_id)
        except Exception as e:
            self.log(f"加载对话失败: {e}", "ERROR")
            # 创建默认对话
            self.create_new_conversation()
    
    def load_chat_history(self):
        """从文件加载聊天记录"""
        if self.chat_history_file.exists():
            try:
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                self.log(f"已加载 {len(history)} 条历史聊天记录", "INFO")
                return history
            except Exception as e:
                self.log(f"加载聊天记录失败: {e}", "WARNING")
                return []
        return []

    def get_effective_base_url(self):
        explicit = (self.config.get("base_url") or "").strip()
        if explicit:
            return explicit
        return get_default_base_url_for_model(self.model_var.get())

    def _format_api_endpoint_for_log(self, url):
        """日志中展示 API 地址（不含密钥、不含查询串）。"""
        if not url:
            return ""
        try:
            p = urlparse(url)
            return f"{p.scheme}://{p.netloc}{p.path or ''}"
        except Exception:
            return "(无法解析的 URL)"

    def _log_config_loaded(self):
        m = self.config.get("model", "")
        eff = self.get_effective_base_url()
        ep = self._format_api_endpoint_for_log(eff) if eff else "(无法根据当前模型推断端点，请在设置中填写 base_url)"
        self.log(f"应用就绪 | 当前模型: {m} | 请求端点: {ep}", "INFO")
    
    def check_for_updates(self):
        """检查是否有更新"""
        try:
            # 读取本地版本
            version_file = Path(data_path("version.txt"))
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    local_version = f.read().strip()
            else:
                # 默认版本
                local_version = "v1.0.0"
                with open(version_file, 'w', encoding='utf-8') as f:
                    f.write(local_version)
            
            # 获取远程版本
            response = requests.get("https://api.github.com/repos/Tian-Technology/AICoder/releases/latest", timeout=5)
            response.raise_for_status()
            release_data = response.json()
            remote_version = release_data.get("tag_name", "v1.0.0")
            release_notes = release_data.get("body", "暂无更新信息")
            
            # 更新UI上的版本信息和更新内容
            def update_ui():
                if hasattr(self, 'latest_version_var'):
                    self.latest_version_var.set(remote_version)
                if hasattr(self, 'update_content_var'):
                    self.update_content_var.set(release_notes)
            
            self.root.after(0, update_ui)
            
            # 检查是否需要更新
            if remote_version != local_version:
                # 查找下载链接
                download_url = None
                for asset in release_data.get("assets", []):
                    if asset.get("name", "").endswith(('.zip', '.exe')):
                        download_url = asset.get("browser_download_url")
                        break
                
                if download_url:
                    # 询问用户是否更新
                    self.root.after(0, lambda: self.ask_update(remote_version, local_version, download_url))
        except Exception as e:
            # 更新UI上的错误信息
            def update_ui_error():
                if hasattr(self, 'latest_version_var'):
                    self.latest_version_var.set("检查失败")
                if hasattr(self, 'update_content_var'):
                    self.update_content_var.set(f"检查更新失败: {str(e)}")
            
            self.root.after(0, update_ui_error)
            # 静默失败，不影响正常启动
            self.log(f"检查更新失败: {e}", "WARNING")
    
    def ask_update(self, remote_version, local_version, download_url):
        """询问用户是否更新"""
        if messagebox.askyesno(
            "发现更新", 
            f"当前版本: {local_version}\n最新版本: {remote_version}\n\n是否更新到最新版本？"
        ):
            self.log(f"用户确认更新到版本: {remote_version}", "INFO")
            # 下载更新
            threading.Thread(target=self.download_update, args=(download_url,), daemon=True).start()
    
    def download_update(self, download_url):
        """下载更新包"""
        try:
            self.log(f"开始下载更新: {download_url}", "INFO")
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            # 下载文件
            file_name = os.path.basename(download_url)
            file_path = os.path.join(temp_dir, file_name)
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.log(f"更新包下载完成: {file_path}", "INFO")
            
            # 解压 zip 文件
            extract_dir = os.path.join(temp_dir, "extract")
            os.makedirs(extract_dir, exist_ok=True)
            
            if file_name.endswith('.zip'):
                shutil.unpack_archive(file_path, extract_dir)
                self.log(f"更新包解压完成: {extract_dir}", "INFO")
            elif file_name.endswith('.exe'):
                # 如果是 exe 文件，直接复制到解压目录
                shutil.copy2(file_path, extract_dir)
                self.log(f"更新包复制完成: {extract_dir}", "INFO")
            
            # 生成更新脚本
            self.generate_update_script(extract_dir)
            
        except Exception as e:
            self.log(f"下载更新失败: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("更新失败", f"下载更新包失败: {str(e)}"))
    
    def generate_update_script(self, extract_dir):
        """生成更新脚本"""
        try:
            # 获取当前 exe 路径
            current_exe = sys.executable
            exe_dir = os.path.dirname(current_exe)
            exe_name = os.path.basename(current_exe)
            
            # 创建更新脚本
            script_path = os.path.join(os.path.dirname(current_exe), "update.bat")
            
            # 构建脚本内容
            script_content = fr"""
@echo off

:: 等待当前程序退出
ping 127.0.0.1 -n 3 > nul

:: 复制新文件
xcopy "{extract_dir}\*" "{exe_dir}" /E /Y /I

:: 保留用户配置
if exist "{exe_dir}\config.json" (
    echo 保留用户配置文件
)

:: 删除临时文件
rmdir /s /q "{os.path.dirname(extract_dir)}"

:: 重新启动程序
start "" "{current_exe}"

:: 删除自身
del "%~f0"
"""
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            self.log(f"更新脚本生成完成: {script_path}", "INFO")
            
            # 执行更新脚本
            self.execute_update(script_path)
            
        except Exception as e:
            self.log(f"生成更新脚本失败: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("更新失败", f"生成更新脚本失败: {str(e)}"))
    
    def execute_update(self, script_path):
        """执行更新脚本"""
        try:
            self.log(f"执行更新脚本: {script_path}", "INFO")
            
            # 启动更新脚本
            subprocess.Popen(script_path, shell=True)
            
            # 退出当前程序
            self.root.after(1000, self.root.destroy)
            
        except Exception as e:
            self.log(f"执行更新脚本失败: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("更新失败", f"执行更新脚本失败: {str(e)}"))

    def get_model_name(self):
        """获取模型显示名称"""
        return get_model_display_name(self.model_var.get())
    
    def calculate_used_tokens(self):
        """计算已使用的token数"""
        total_tokens = 0
        for timestamp, sender, message in self.chat_history:
            # 简单估算：按字符数的1/4计算token数
            total_tokens += len(message) // 4
        return total_tokens
    
    def update_context_info(self):
        """更新上下文窗口信息"""
        if hasattr(self, 'context_label'):
            used_tokens = self.calculate_used_tokens()
            model = self.model_var.get()
            max_tokens = get_model_max_tokens(model)
            remaining_tokens = max_tokens - used_tokens
            
            # 根据剩余token数设置不同的样式
            if remaining_tokens < 0:
                style = "Red.TLabel"
            elif remaining_tokens < max_tokens * 0.2:
                style = "Orange.TLabel"
            else:
                style = "Green.TLabel"
            
            context_info = f"上下文窗口: 已使用 {used_tokens} / {max_tokens} tokens (剩余 {remaining_tokens} tokens)"
            self.context_label.config(text=context_info, style=style)
    
    def update_usage_display(self):
        """更新 API 用量显示"""
        if hasattr(self, 'usage_label'):
            monthly_usage = self.config.get('monthly_usage', 0)
            current_month = self.config.get('current_month', datetime.now().strftime("%Y-%m"))
            usage_info = f"API 用量: 本月已使用 {monthly_usage} tokens ({current_month})"
            self.usage_label.config(text=usage_info)

    def send_message(self):
        """发送消息"""
        user_message = self.input_text.get("1.0", tk.END).strip()
        if not user_message:
            messagebox.showwarning("警告", "请输入消息内容！")
            return
        
        # 显示用户消息
        self.add_message_to_display("用户", user_message)
        preview = user_message if len(user_message) <= 400 else user_message[:400] + "…"
        self.log(f"用户发送（{len(user_message)} 字）: {preview}", "INFO")
        self.input_text.delete("1.0", tk.END)
        
        # 禁用发送按钮，防止重复发送
        send_btn = getattr(self, "send_button", None)
        if send_btn:
            send_btn.config(state=tk.DISABLED)

        # 在新线程中发送请求
        threading.Thread(target=self.process_message, args=(user_message, send_btn), daemon=True).start()

    def process_message(self, user_message, send_btn):
        """处理消息（在新线程中执行，流式拉取并在主线程刷新 UI）"""
        start_time = time.time()
        stream_begun = False
        full_response = ""
        total_tokens = 0
        try:
            # 重置停止标志
            self._stop_generation = False
            self.root.after(0, lambda: self._toggle_generation_buttons(True))
            
            model_name = self.model_var.get()
            api_key = (self.config.get("api_key") or "").strip()
            base_url = self.get_effective_base_url()
            if not base_url:
                raise ValueError(
                    "无法确定 API 地址：请在设置中填写完整 base_url，或选择已支持自动端点的模型"
                    "（deepseek- / gpt- / glm- / qwen- / moonshot- / kimi- 等）。"
                )

            messages = []
            for _ts, snd, msg in self.chat_history:
                if snd in ("用户", "user"):
                    messages.append({"role": "user", "content": msg})
                elif snd in ("AI", "assistant"):
                    messages.append({"role": "assistant", "content": msg})

            ep = self._format_api_endpoint_for_log(base_url)
            self.log(f"流式请求开始 | model={model_name} | endpoint={ep} | 上下文消息数={len(messages)}", "INFO")

            # 保存旧的 update_api_usage 方法，临时替换为记录 token 数
            old_update_api_usage = self.update_api_usage
            def temp_update_api_usage(tokens):
                nonlocal total_tokens
                total_tokens = tokens
                old_update_api_usage(tokens)
            
            self.update_api_usage = temp_update_api_usage
            
            gen = self.call_ai_api(messages, model_name, api_key, base_url, stream=True)
            self.root.after(0, self._begin_ai_stream_ui)
            stream_begun = True
            self.log("开始接收流式响应", "INFO")
            chunk_count = 0
            for chunk in gen:
                # 检查是否停止生成
                if self._stop_generation:
                    self.log("用户停止生成", "INFO")
                    break
                if chunk:
                    chunk_count += 1
                    self.log(f"接收到第 {chunk_count} 个chunk，长度: {len(chunk)}", "INFO")
                    full_response += chunk
                    # 直接在主线程中更新UI，确保实时显示
                    self.root.after_idle(lambda c=chunk: self._append_ai_stream_chunk(c))
                    # 增加一个小延迟，确保UI有时间更新
                    time.sleep(0.01)
            
            # 如果是用户停止的，添加停止标记
            if self._stop_generation:
                full_response += "\n\n【用户已停止生成】"
            
            elapsed = time.time() - start_time
            self.log(
                f"流式完成 | model={model_name} | 输出约 {len(full_response)} 字符 | 消耗 {total_tokens} tokens | {elapsed:.2f}s",
                "INFO",
            )
            self.root.after(0, lambda t=full_response, e=elapsed, tt=total_tokens: self._finish_ai_stream_ui(t, e, tt))
            # 恢复原始方法
            self.update_api_usage = old_update_api_usage
        except Exception as e:
            elapsed = time.time() - start_time
            self.log(f"消息处理异常: {e} | {elapsed:.2f}s", "ERROR")
            if stream_begun:
                self.root.after(0, lambda m=str(e), et=elapsed: self._fail_ai_stream_ui(m, et))
            else:
                error_msg = f"API 调用失败: {str(e)}\n【响应时间: {elapsed:.2f} 秒】"
                self.root.after(0, lambda em=error_msg: self.add_message_to_display("系统", em))
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self._toggle_generation_buttons(False))
            if send_btn and hasattr(send_btn, "config"):
                try:
                    if send_btn.winfo_exists():
                        self.root.after(0, lambda b=send_btn: b.config(state=tk.NORMAL))
                except Exception as e:
                    self.log(f"恢复发送按钮状态失败: {e}", "DEBUG")
    
    def stop_generation(self):
        """停止生成"""
        self._stop_generation = True
        self.log("用户点击停止生成", "INFO")
    
    def _toggle_generation_buttons(self, is_generating):
        """切换生成按钮状态"""
        try:
            if hasattr(self, 'send_button'):
                try:
                    if self.send_button.winfo_exists():
                        self.send_button.config(state=tk.DISABLED if is_generating else tk.NORMAL)
                except Exception:
                    pass
            if hasattr(self, 'stop_button'):
                try:
                    if self.stop_button.winfo_exists():
                        self.stop_button.config(state=tk.NORMAL if is_generating else tk.DISABLED)
                except Exception:
                    pass
        except Exception as e:
            self.log(f"切换按钮状态失败: {e}", "ERROR")

    def _begin_ai_stream_ui(self):
        """主线程：开始一条 AI 流式回复的展示（创建临时文本区域用于流式显示）"""
        self._stream_reply_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留三位毫秒
        self._streaming_reply_buffer = ""
        
        # 获取历史区域
        history_frame = None
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and widget.cget("text") == "对话历史":
                history_frame = widget
                break
        
        if history_frame:
            # 隐藏 tk.Text，显示临时文本区域
            self.chat_display.pack_forget()
            
            # 创建临时文本区域用于流式显示
            # 根据当前主题设置合适的背景和前景色
            if sv_ttk.get_theme() == "dark":
                bg_color = "#2d2d2d"
                fg_color = "#e0e0e0"
            else:
                bg_color = "#ffffff"
                fg_color = "#333333"
            
            self._stream_text = tk.Text(history_frame, 
                                       wrap=tk.WORD,
                                       font=('微软雅黑', 10),
                                       padx=10,
                                       pady=10,
                                       bg=bg_color,
                                       fg=fg_color)
            self._stream_text.pack(fill=tk.BOTH, expand=True)
            
            # 插入标题
            self._stream_text.insert(tk.END, f"[{self._stream_reply_ts}] AI:\n", "title")
            self._stream_text.tag_config("title", foreground="blue", font=('微软雅黑', 10, 'bold'))
            self._stream_text.see(tk.END)
            self._stream_text.update_idletasks()  # 强制更新UI

    def _append_ai_stream_chunk(self, chunk):
        """主线程：追加一段模型输出到临时文本区域"""
        if not chunk:
            return
        
        self._streaming_reply_buffer = getattr(self, "_streaming_reply_buffer", "") + chunk
        
        # 实时更新到临时文本区域
        if hasattr(self, '_stream_text') and self._stream_text.winfo_exists():
            try:
                # 插入文本
                self._stream_text.insert(tk.END, chunk)
                # 滚动到末尾
                self._stream_text.see(tk.END)
                # 强制更新UI，确保流畅的流式效果
                self._stream_text.update_idletasks()
                # 也更新主窗口，确保整个界面都能及时响应
                self.root.update_idletasks()
                # 日志记录UI更新
                self.log(f"UI更新：追加了 {len(chunk)} 个字符", "DEBUG")
            except Exception as e:
                self.log(f"UI更新失败: {e}", "ERROR")

    def _finish_ai_stream_ui(self, full_text, elapsed_sec, total_tokens=0):
        """主线程：流式结束，移除临时文本区域，显示文本内容"""
        try:
            timing = f"\n\n【响应时间: {elapsed_sec:.2f} 秒】【该轮对话消耗token：{total_tokens}】"
            stored = full_text + timing
            
            # 移除临时文本区域
            if hasattr(self, '_stream_text'):
                try:
                    if self._stream_text.winfo_exists():
                        self._stream_text.destroy()
                except Exception:
                    pass
                finally:
                    if hasattr(self, '_stream_text'):
                        delattr(self, '_stream_text')
            
            # 显示 tk.Text
            if hasattr(self, 'chat_display'):
                try:
                    if self.chat_display.winfo_exists():
                        self.chat_display.pack(fill=tk.BOTH, expand=True)
                        
                        # 重新显示所有消息
                        self.chat_display.config(state=tk.NORMAL)
                        self.chat_display.delete("1.0", tk.END)
                        
                        for timestamp, sender, message in self.chat_history:
                            if sender == "AI":
                                self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "ai")
                                self.chat_display.insert(tk.END, f"{message}\n\n")
                            elif sender == "用户":
                                self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "user")
                                self.chat_display.insert(tk.END, f"{message}\n\n")
                            else:
                                self.chat_display.insert(tk.END, f"[{timestamp}] {sender}:\n", "system")
                                self.chat_display.insert(tk.END, f"{message}\n\n")
                        
                        # 添加当前消息
                        ts = getattr(self, "_stream_reply_ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])  # 保留三位毫秒
                        self.chat_display.insert(tk.END, f"[{ts}] AI:\n", "ai")
                        self.chat_display.insert(tk.END, f"{stored}\n\n")
                        
                        self.chat_display.config(state=tk.DISABLED)
                        self.chat_display.see(tk.END)
                except Exception as e:
                    self.log(f"更新聊天显示失败: {e}", "ERROR")
            
            # 检查是否已经添加过相同的消息，避免重复
            if not self.chat_history or self.chat_history[-1][1:] != ("AI", stored):
                ts = getattr(self, "_stream_reply_ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])  # 保留三位毫秒
                self.chat_history.append((ts, "AI", stored))
                # 自动保存聊天记录
                self.save_chat_history()
            
            if hasattr(self, "update_context_info"):
                try:
                    self.update_context_info()
                except Exception:
                    pass
        except Exception as e:
            self.log(f"完成流式UI失败: {e}", "ERROR")

    def _fail_ai_stream_ui(self, err_msg, elapsed_sec):
        """主线程：已开始流式 UI 后发生异常时的收尾"""
        tail = f"\n\n[请求异常: {err_msg}]【响应时间: {elapsed_sec:.2f} 秒】\n"
        cd = getattr(self, "chat_display", None)
        ts = getattr(self, "_stream_reply_ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        buf = getattr(self, "_streaming_reply_buffer", "")
        if cd:
            try:
                if cd.winfo_exists():
                    cd.config(state=tk.NORMAL)
                    cd.insert(tk.END, tail, "message")
                    cd.insert(tk.END, "-" * 50 + "\n", "separator")
                    cd.see(tk.END)
                    cd.config(state=tk.DISABLED)
            except tk.TclError:
                pass
        self.chat_history.append((ts, "系统", buf + tail))
        
        # 自动保存聊天记录
        self.save_chat_history()
        
        if hasattr(self, "update_context_info"):
            self.update_context_info()

    def _refresh_log_widget(self, log_entry):
        """主线程：若当前正在查看日志页，追加一行。"""
        try:
            w = getattr(self, "_log_scrolled", None)
            if not w:
                return
            try:
                if not w.winfo_exists():
                    return
            except tk.TclError:
                return
            w.config(state=tk.NORMAL)
            body = w.get("1.0", tk.END).strip()
            if body == "暂无日志记录":
                w.delete("1.0", tk.END)
            w.insert(tk.END, log_entry + "\n")
            w.see(tk.END)
            w.config(state=tk.DISABLED)
        except Exception as e:
            # 日志更新失败，不影响其他功能
            pass

    def log(self, message, level="INFO"):
        """记录运行日志；可在工作线程中调用，内部会派发到主线程更新列表与日志页。"""
        import inspect
        # 获取调用者信息
        caller_frame = inspect.currentframe().f_back
        caller_info = inspect.getframeinfo(caller_frame)
        file_name = os.path.basename(caller_info.filename)
        line_number = caller_info.lineno
        
        def _append():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留三位毫秒
            thread_name = threading.current_thread().name
            log_entry = f"[{timestamp}] [{level}] [Thread: {thread_name}] [{file_name}:{line_number}] {message}"
            print(log_entry)
            self.logs.append(log_entry)
            while len(self.logs) > self._max_log_entries:
                self.logs.pop(0)
            self._refresh_log_widget(log_entry)

        if threading.current_thread() is threading.main_thread():
            _append()
        else:
            self.root.after(0, _append)
    
    def debug(self, message):
        """记录DEBUG级别的日志"""
        self.log(message, "DEBUG")
    
    def trace(self, message):
        """记录TRACE级别的日志"""
        self.log(message, "TRACE")
    
    def call_ai_api(self, messages, model_name, api_key, base_url, stream=False):
        """
        调用 AI API。非流式直接返回 str；流式返回生成器（供 for 迭代），
        不可把含 yield 的分支与 return 混在同一函数里，否则 stream=False 也会得到 generator 对象。
        """
        # 检查是否是 Claude 模型
        is_claude = model_name.startswith("claude")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        
        # 构建请求体
        if is_claude:
            # Claude 模型的请求格式
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": stream,
            }
        else:
            # OpenAI 兼容格式
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": stream,
            }

        if not stream:
            try:
                self.log(f"开始非流式 API 调用 | model={model_name} | endpoint={self._format_api_endpoint_for_log(base_url)}", "INFO")
                start_time = time.time()
                response = requests.post(base_url, headers=headers, json=payload, timeout=60)
                elapsed = time.time() - start_time
                self.log(f"API 响应 | status={response.status_code} | time={elapsed:.2f}s", "INFO")
                response.raise_for_status()
                result = response.json()
                # 更新 API 用量
                if "usage" in result:
                    total_tokens = result["usage"].get("total_tokens", 0)
                    if total_tokens > 0:
                        self.update_api_usage(total_tokens)
                        self.log(f"API 用量 | total_tokens={total_tokens}", "INFO")
                # 处理不同模型的响应格式
                if is_claude:
                    # Claude 模型的响应格式
                    content = result["content"][0]["text"]
                else:
                    # OpenAI 兼容格式
                    content = result["choices"][0]["message"]["content"]
                self.log(f"API 调用完成 | content_length={len(content)} | time={elapsed:.2f}s", "INFO")
                return content
            except Exception as e:
                self.log(f"API 非流式调用失败: {e}", "ERROR")
                return f"API 调用错误：{str(e)}"

        def _stream_gen():
            total_tokens = 0
            start_time = time.time()
            try:
                self.log(f"开始流式 API 调用 | model={model_name} | endpoint={self._format_api_endpoint_for_log(base_url)}", "INFO")
                resp = requests.post(base_url, headers=headers, json=payload, stream=True, timeout=60)
                elapsed = time.time() - start_time
                self.log(f"API 已响应 HTTP {resp.status_code}（流式） | time={elapsed:.2f}s", "INFO")
                resp.raise_for_status()
                chunk_count = 0
                total_content_length = 0
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk_count += 1
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        if data_str.strip() == "[DONE]":
                            # 流式响应结束，更新用量
                            if total_tokens > 0:
                                self.update_api_usage(total_tokens)
                                self.log(f"API 用量 | total_tokens={total_tokens}", "INFO")
                            elapsed = time.time() - start_time
                            self.log(f"流式 API 调用完成 | chunks={chunk_count} | content_length={total_content_length} | time={elapsed:.2f}s", "INFO")
                            break
                        try:
                            data_json = json.loads(data_str)
                            # 检查是否有 usage 信息
                            if "usage" in data_json:
                                total_tokens = data_json["usage"].get("total_tokens", 0)
                            # 处理不同模型的响应格式
                            if is_claude:
                                # Claude 模型的流式响应格式
                                if "delta" in data_json:
                                    delta = data_json["delta"]
                                    if "text" in delta:
                                        content = delta["text"]
                                        if content:
                                            total_content_length += len(content)
                                            if chunk_count % 10 == 0:  # 每10个chunk记录一次
                                                self.log(f"流式响应 | chunk={chunk_count} |累计长度={total_content_length}", "DEBUG")
                                            yield content
                            else:
                                # OpenAI 兼容格式
                                choices = data_json.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        total_content_length += len(content)
                                        if chunk_count % 10 == 0:  # 每10个chunk记录一次
                                            self.log(f"流式响应 | chunk={chunk_count} |累计长度={total_content_length}", "DEBUG")
                                        yield content
                        except json.JSONDecodeError as e:
                            self.log(f"JSON 解析失败: {e}", "DEBUG")
                            if data_str.strip():
                                yield data_str
                    elif decoded_line.startswith("{"):
                        try:
                            data_json = json.loads(decoded_line)
                            # 处理不同模型的响应格式
                            if is_claude:
                                # Claude 模型的响应格式
                                if "content" in data_json:
                                    for item in data_json["content"]:
                                        if "text" in item:
                                            content = item["text"]
                                            if content:
                                                total_content_length += len(content)
                                                yield content
                            else:
                                # OpenAI 兼容格式
                                choices = data_json.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        total_content_length += len(content)
                                        yield content
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                elapsed = time.time() - start_time
                self.log(f"API 流式连接/读取失败: {e} | time={elapsed:.2f}s", "ERROR")
                yield f"API 调用错误：{str(e)}"

        return _stream_gen()

    def render_markdown(self, text):
        """渲染 Markdown 格式为 HTML"""
        # 使用 markdown 库将 Markdown 转换为 HTML
        html = markdown.markdown(text)
        return html
    
    def search_chat(self):
        """搜索对话内容并高亮显示"""
        search_text = self.search_var.get().strip()
        if not search_text:
            return
        
        # 清除之前的高亮
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
        
        # 搜索并高亮匹配的文本
        start_pos = "1.0"
        count = 0
        while True:
            start_pos = self.chat_display.search(search_text, start_pos, tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_text)}c"
            self.chat_display.tag_add("highlight", start_pos, end_pos)
            start_pos = end_pos
            count += 1
        
        # 显示搜索结果数量
        if count > 0:
            messagebox.showinfo("搜索结果", f"找到 {count} 个匹配项")
        else:
            messagebox.showinfo("搜索结果", "未找到匹配项")
    
    def clear_search(self):
        """清除搜索高亮"""
        self.search_var.set("")
        self.chat_display.tag_remove("highlight", "1.0", tk.END)
    
    def add_message_to_display(self, role, content):
        """追加消息到 chat_display 与 chat_history（用户/系统等非流式一条）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留三位毫秒
        role_labels = {"用户": "用户", "user": "用户", "AI": "AI", "assistant": "AI", "系统": "系统"}
        sender = role_labels.get(role, role)
        self.chat_history.append((timestamp, sender, content))
        
        # 自动保存聊天记录
        self.save_chat_history()
        
        if hasattr(self, "chat_display") and self.chat_display:
            # 重新显示所有消息
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            
            for ts, snd, msg in self.chat_history:
                if snd == "AI":
                    self.chat_display.insert(tk.END, f"[{ts}] {snd}:\n", "ai")
                    self.chat_display.insert(tk.END, f"{msg}\n\n")
                elif snd == "用户":
                    self.chat_display.insert(tk.END, f"[{ts}] {snd}:\n", "user")
                    self.chat_display.insert(tk.END, f"{msg}\n\n")
                else:
                    self.chat_display.insert(tk.END, f"[{ts}] {snd}:\n", "system")
                    self.chat_display.insert(tk.END, f"{msg}\n\n")
            
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)
        if hasattr(self, "update_context_info"):
            self.update_context_info()

if __name__ == "__main__":
    root = tk.Tk()
    app = AICoderApp(root)
    root.mainloop()