import gradio as gr
from modules import script_callbacks
from pathlib import Path
import sys

# 添加 scripts 目录到系统路径
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.append(str(scripts_dir))

# 导入各个功能模块
try:
    from prompt_templates import create_prompt_template_ui
except ImportError:
    create_prompt_template_ui = None
    print("Warning: Could not import prompt_templates")

try:
    from quick_description import create_quick_description
except ImportError:
    create_quick_description = None
    print("Warning: Could not import quick_description")

try:
    from tag_management import create_tag_management_module
except ImportError:
    create_tag_management_module = None
    print("Warning: Could not import tag_management")

try:
    from image_management import create_image_management_module
except ImportError:
    create_image_management_module = None
    print("Warning: Could not import image_management")


def vision_chat_tab():
    """创建图像识别与语言交互标签页"""
    with gr.Blocks(analytics_enabled=False) as ui:
        with gr.Tabs():
            # 图像识别与语言交互标签页
            with gr.TabItem("2 图像识别与语言交互"):
                with gr.Row():
                    # 左侧区域：标签管理、图像管理、模型选择
                    with gr.Column(scale=1):
                        # 标签管理模块
                        try:
                            if create_tag_management_module is not None:
                                tag_management_components = create_tag_management_module()
                                if tag_management_components:
                                    with gr.Box():
                                        if "refresh_button" in tag_management_components:
                                            tag_management_components["refresh_button"]
                                        if "folder_path" in tag_management_components:
                                            tag_management_components["folder_path"].elem_classes = ["xykc-accordion"]
                            else:
                                gr.Markdown("标签管理模块当前不可用。")
                        except Exception as e:
                            print(f"标签管理模块加载失败：{e}")
                        
                        # 图像管理模块
                        try:
                            if create_image_management_module is not None:
                                image_management_ui = create_image_management_module()
                                if image_management_ui:
                                    with gr.Box():
                                        if "dir_input" in image_management_ui:
                                            image_management_ui["dir_input"]
                                        if "load_dir_btn" in image_management_ui:
                                            image_management_ui["load_dir_btn"]
                                        if "gallery" in image_management_ui:
                                            image_management_ui["gallery"]
                            else:
                                gr.Markdown("图像管理模块当前不可用。")
                        except Exception as e:
                            print(f"图像管理模块加载失败：{e}")
                        
                        # 模型选择区域
                        with gr.Group():
                            gr.Markdown("### 模型选择")
                            gr.Markdown("📌 **模型选择建议**：8GB 显存选择 2B，12GB-16GB 显存可选择 4B-9B 模型")
                            
                            model_type = gr.Radio(
                                [("视觉模型", "vision"), ("语言模型", "text")],
                                value="vision",
                                label="模型类型",
                                interactive=True,
                                info="视觉模型支持图片识别和纯文本聊天，语言模型仅支持文本对话"
                            )
                            
                            vision_model = gr.Dropdown(
                                label="视觉模型",
                                choices=["qwen3.5:9b", "qwen3.5:4b", "qwen3-vl:8b", "qwen3-vl:4b", "qwen3-vl:2b"],
                                value="qwen3.5:9b",
                                interactive=True,
                                info="选择视觉模型（支持图片识别 + 文本聊天）",
                                scale=2,
                                elem_classes="larger-text",
                                container=True
                            )
                            
                            language_model = gr.Dropdown(
                                label="语言模型",
                                choices=["qwen3:latest", "qwen3.5:4b", "deepseek-r1:8b"],
                                value="qwen3:latest",
                                interactive=False,
                                info="选择语言模型",
                                scale=2,
                                elem_classes="larger-text",
                                container=True
                            )
                    
                    # 右侧区域：关键词辅助模板和聊天区域
                    with gr.Column(scale=1):
                        # 关键词辅助模板区域
                        with gr.Accordion("关键词辅助模板", open=False):
                            if create_prompt_template_ui is not None:
                                template_ui = create_prompt_template_ui()
                                with gr.Row():
                                    with gr.Column():
                                        template_ui["expression_template"]
                                    with gr.Column():
                                        template_ui["story_template"]
                                    with gr.Column():
                                        template_ui["shot_template"]
                            else:
                                gr.Markdown("关键词辅助模板模块当前不可用。")
                        
                        # 聊天区域
                        chat_history = gr.Chatbot(
                            elem_id="chatbot", 
                            label="聊天记录", 
                            height=300,
                            render=True
                        )
                        chat_message = gr.Textbox(
                            show_label=False,
                            placeholder="输入消息或上传图片（支持多轮对话，可上传一次图片后连续提问）",
                            container=True,
                            scale=1,
                            min_width=300,
                            lines=3
                        )
                        with gr.Row(equal_height=True):
                            submit_button = gr.Button(
                                "发送",
                                size="lg",
                                variant="primary",
                                elem_classes="orange-button",
                                scale=2
                            )
                            clear_button = gr.Button(
                                "清空聊天",
                                size="lg", 
                                variant="primary",
                                elem_classes="orange-button",
                                scale=2
                            )
                            save_button = gr.Button(
                                "保存聊天记录",
                                size="lg",
                                variant="primary",
                                elem_classes="orange-button",
                                scale=2
                            )
                            copy_button = gr.Button(
                                "复制最新回复",
                                size="lg",
                                variant="primary",
                                elem_classes="orange-button",
                                scale=2
                            )

                        # 快捷描述区域
                        with gr.Group():
                            # 创建并添加快捷描述按钮
                            if create_quick_description is not None:
                                quick_description_buttons = create_quick_description(chat_message)
                            else:
                                quick_description_buttons = {}
                
                # 添加事件处理
                def on_submit(message, chat_history):
                    """简单的聊天提交处理（需要配合 Ollama API）"""
                    if not message:
                        return "", chat_history
                    chat_history.append((message, "[待实现] 需要集成 Ollama API"))
                    return "", chat_history
                
                chat_message.submit(
                    fn=on_submit,
                    inputs=[chat_message, chat_history],
                    outputs=[chat_message, chat_history]
                )
                submit_button.click(
                    fn=on_submit,
                    inputs=[chat_message, chat_history],
                    outputs=[chat_message, chat_history]
                )
                clear_button.click(lambda: [], outputs=[chat_history])
                
                # 使用 JavaScript 实现复制功能
                copy_button.click(
                    None,
                    inputs=[chat_history],
                    outputs=[],
                    _js="""
                    (chat_history) => {
                        if (chat_history && chat_history.length > 0) {
                            const lastMessage = chat_history[chat_history.length - 1];
                            if (lastMessage && lastMessage.length >= 2) {
                                const aiResponse = lastMessage[1];
                                if (aiResponse && aiResponse.length > 0) {
                                    navigator.clipboard.writeText(aiResponse).then(() => {
                                        alert("最新回复已复制到剪贴板！");
                                    }).catch(err => {
                                        console.error('复制失败：', err);
                                        alert("复制失败，请手动复制");
                                    });
                                    return;
                                }
                            }
                        }
                        alert("没有可复制的回复内容");
                    }
                    """
                )
    
    return [(ui, "图像识别与语言交互", "Vision_Chat_Tab")]


def on_app_started(*args, **kwargs):
    """在 WebUI 启动时显示插件信息"""
    print("=" * 60)
    print("Qwen 图像识别与语言交互插件")
    print("开发者：鸡肉爱土豆")
    print("网址：https://space.bilibili.com/403361177")
    print()
    print("集成功能：")
    print("- Qwen 系列视觉模型对话（支持图片识别）")
    print("- Qwen 系列语言模型对话")
    print("- 关键词辅助模板（表情包/故事/分镜）")
    print("- 标签管理（批量添加/删除关键词）")
    print("- 图像管理（图片预览与管理）")
    print("- 资源汇总与公告")
    print()
    print("前置要求：")
    print("- 需要安装 Ollama 并下载 Qwen 系列模型")
    print("- Ollama 下载地址：https://ollama.com/")
    print("- 模型命令：ollama pull qwen3.5:9b")
    print("=" * 60)


# 注册标签页和启动事件
script_callbacks.on_ui_tabs(vision_chat_tab)
script_callbacks.on_app_started(on_app_started)
