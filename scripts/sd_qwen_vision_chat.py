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
                                choices=["qwen3.5:9b", "qwen3.5:4b", "qwen3-vl:8b", "qwen3-vl:4b", "qwen3.5-abliterated:4B", "huihui_ai/qwen3.5-abliterated:9b"],
                                value="qwen3.5:4b",
                                interactive=True,
                                info="选择视觉模型（支持图片识别 + 文本聊天）",
                                scale=2,
                                elem_classes="larger-text",
                                container=True
                            )
                            
                            language_model = gr.Dropdown(
                                label="语言模型",
                                choices=["qwen3:latest", "qwen3.5:4b", "qwen3.5:9b"],
                                value="qwen3:latest",
                                interactive=False,
                                info="选择语言模型",
                                scale=2,
                                elem_classes="larger-text",
                                container=True
                            )
                        
                        # 图像上传区域（使用 ForgeCanvas 避免权限问题）
                        with gr.Group():
                            gr.Markdown("### 📤 图片上传")
                            gr.Markdown("📌 **使用说明**：Qwen3.5 等多模态模型支持同时上传图片和文字聊天")
                            
                            upload_method = gr.Radio(
                                [("单张图片", "single"), ("批量图片", "batch")],
                                value="single",
                                label="上传方式",
                                interactive=True,
                                scale=2,
                                elem_classes="larger-text",
                                container=True
                            )
                            
                            with gr.Box(visible=True) as image_container:
                                # 使用 ForgeCanvas 代替 gr.Image，避免 Windows 权限问题
                                from modules_forge.forge_canvas.canvas import ForgeCanvas
                                
                                qwen_canvas = ForgeCanvas(
                                    no_upload=False,
                                    no_scribbles=True,  # 关闭涂鸦功能
                                    height=300,
                                    elem_id="qwen_vision_image"
                                )
                                
                                # 使用隐藏的 State 来存储 Canvas 的 background 值
                                image_input = qwen_canvas.background
                                
                                # 批量上传仍然使用 Files（仅在需要时启用）
                                multi_images_input = gr.Files(
                                    type="filepath",
                                    label="多张图片输入",
                                    visible=False,
                                    height=300,
                                    scale=1,
                                    min_width=300,
                                    file_count="multiple",
                                    file_types=["image"]
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
                        
                        # 隐藏的状态组件：保存最后使用的图片路径
                        last_image_path_state = gr.State(value=None)
                        
                        chat_message = gr.Textbox(
                            show_label=False,
                            placeholder="输入消息（支持多轮对话，可上传一次图片后连续提问）",
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
                            if create_quick_description is not None:
                                quick_description_buttons = create_quick_description(chat_message)
                            else:
                                quick_description_buttons = {}
                
                # 添加 Ollama API 配置
                with gr.Accordion("⚙️ Ollama API 配置", open=False):
                    ollama_host = gr.Textbox(
                        label="Ollama 服务器地址",
                        value="http://localhost:11434",
                        placeholder="http://localhost:11434",
                        info="Ollama API 服务器地址"
                    )
                    ollama_timeout = gr.Number(
                        label="超时时间（秒）",
                        value=300,
                        minimum=60,
                        maximum=3600,
                        step=60,
                        info="请求超时时间，默认 300 秒"
                    )
                
                # 添加 Ollama API 调用函数
                import sys
                import os
                from pathlib import Path
                
                # 添加 ollama 目录到 Python 路径
                extension_dir = Path(__file__).parent.parent
                ollama_dir = extension_dir / "ollama"
                if str(ollama_dir) not in sys.path:
                    sys.path.insert(0, str(ollama_dir))
                
                try:
                    from ollama_api import get_response_lvm_ollama_api, get_response_text_ollama_api
                    OLLAMA_AVAILABLE = True
                except ImportError as e:
                    print(f"警告：无法导入 Ollama API 模块：{e}")
                    OLLAMA_AVAILABLE = False
                
                def base64_to_image_file(base64_str, output_path):
                    """将 Base64 字符串保存为图片文件"""
                    import base64
                    if base64_str.startswith("data:image/png;base64,"):
                        base64_str = base64_str.replace("data:image/png;base64,", "")
                    
                    image_data = base64.b64decode(base64_str)
                    
                    # 确保目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    
                    return output_path
                
                # 简化的聊天处理函数（集成 Ollama API）
                def on_chat(message, chat_history, vision_model, language_model, model_type, 
                           upload_method, image_input, multi_images_input, ollama_host, ollama_timeout):
                    """聊天处理函数（集成 Ollama API）"""
                    print(f"\n=== 调试信息 ===")
                    print(f"message: {message}")
                    print(f"upload_method: {upload_method}")
                    print(f"image_input type: {type(image_input)}")
                    print(f"multi_images_input: {multi_images_input}")
                    print(f"model_type: {model_type}")
                    
                    if not message and not image_input and not multi_images_input:
                        return "", chat_history
                    
                    # 判断是否有图片
                    has_image = False
                    image_count = 0
                    temp_image_paths = []
                    
                    # 处理 ForgeCanvas 的图片（可能是 PIL 对象或 Base64 字符串）
                    if upload_method == "single" and image_input:
                        has_image = True
                        image_count = 1
                        
                        # 将图片保存为临时文件
                        try:
                            temp_dir = os.path.join(extension_dir, "tmp", "qwen_uploads")
                            os.makedirs(temp_dir, exist_ok=True)
                            temp_path = os.path.join(temp_dir, f"temp_{os.urandom(4).hex()}.png")
                            
                            # 如果是 PIL 对象
                            if hasattr(image_input, 'save'):
                                # 转换为 RGB 模式（移除 alpha 通道）
                                if image_input.mode == 'RGBA':
                                    image_input = image_input.convert('RGB')
                                image_input.save(temp_path)
                                temp_image_paths.append(temp_path)
                                print(f"✓ 已保存 PIL 图片：{temp_path}")
                            # 如果是 Base64 字符串
                            elif isinstance(image_input, str) and image_input.startswith("data:image"):
                                base64_to_image_file(image_input, temp_path)
                                temp_image_paths.append(temp_path)
                                print(f"✓ 已保存 Base64 图片：{temp_path}")
                            else:
                                print(f"⚠ image_input 格式不正确：{type(image_input)}")
                                has_image = False
                        except Exception as e:
                            print(f"❌ 保存图片失败：{e}")
                            has_image = False
                    
                    # 处理批量上传
                    elif upload_method == "batch" and multi_images_input:
                        has_image = True
                        if isinstance(multi_images_input, list):
                            image_count = len(multi_images_input)
                            temp_image_paths.extend([f for f in multi_images_input if isinstance(f, str)])
                        else:
                            image_count = 1
                            if isinstance(multi_images_input, str):
                                temp_image_paths.append(multi_images_input)
                    
                    print(f"has_image: {has_image}, image_count: {image_count}, temp_paths: {len(temp_image_paths)}")
                    
                    # 构建消息
                    user_message = message
                    if has_image:
                        if image_count == 1:
                            user_message = f"[图片] {message}" if message else "[图片]"
                        else:
                            user_message = f"[{image_count}张图片] {message}" if message else f"[{image_count}张图片]"
                    
                    # 添加到聊天记录（先显示用户消息）
                    if user_message:
                        chat_history.append((user_message, ""))
                    
                    # 调用 Ollama API
                    ai_response = ""
                    if OLLAMA_AVAILABLE:
                        try:
                            # 选择模型
                            model_name = vision_model if model_type == "vision" else language_model
                            
                            # 根据是否有图片选择函数
                            if has_image and temp_image_paths and model_type == "vision":
                                # 视觉模型 - 使用第一张图片
                                print(f"📷 调用视觉模型：{model_name}, 图片路径：{temp_image_paths[0]}")
                                ai_response = get_response_lvm_ollama_api(
                                    input_model_name=model_name,
                                    input_content=message or "请描述这张图片",
                                    input_image_path=temp_image_paths[0]
                                )
                            else:
                                # 语言模型或纯文本
                                print(f"💬 调用语言模型：{model_name}")
                                ai_response = get_response_text_ollama_api(
                                    input_model_name=model_name,
                                    input_content=message or "你好！有什么可以帮助你的？"
                                )
                            
                            if not ai_response:
                                ai_response = "[错误] API 返回空响应"
                        
                        except Exception as e:
                            ai_response = f"[错误] {str(e)}"
                            print(f"❌ Ollama API 调用失败：{e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        ai_response = "[未安装] 请先安装 ollama 包：pip install ollama"
                    
                    print(f"✅ AI 回复：{ai_response[:100]}...")
                    print("=================\n")
                    
                    # 更新聊天记录中的 AI 回复
                    if chat_history and chat_history[-1][0] == user_message:
                        chat_history[-1] = (user_message, ai_response)
                    
                    # 清理临时文件
                    for temp_path in temp_image_paths:
                        try:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                        except:
                            pass
                    
                    return "", chat_history
                
                # 聊天事件绑定
                chat_inputs = [chat_message, chat_history, vision_model, language_model, 
                              model_type, upload_method, image_input, multi_images_input, 
                              ollama_host, ollama_timeout]
                chat_outputs = [chat_message, chat_history]

                chat_message.submit(on_chat, inputs=chat_inputs, outputs=chat_outputs)
                submit_button.click(on_chat, inputs=chat_inputs, outputs=chat_outputs)
                clear_button.click(lambda: [], outputs=[chat_history])
                
                # 上传方式切换事件
                def switch_upload(method):
                    """切换上传方式"""
                    if method == "single":
                        return gr.update(visible=True), gr.update(visible=False)
                    else:
                        return gr.update(visible=False), gr.update(visible=True)
                
                upload_method.change(
                    fn=switch_upload,
                    inputs=[upload_method],
                    outputs=[image_input, multi_images_input]
                )
                
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
    print()
    print("前置要求：")
    print("- 需要安装 Ollama 并下载 Qwen 系列模型")
    print("- Ollama 下载地址：https://ollama.com/")
    print("- 模型命令：ollama pull qwen3.5:9b")
    print("=" * 60)


# 注册标签页和启动事件
script_callbacks.on_ui_tabs(vision_chat_tab)
script_callbacks.on_app_started(on_app_started)
