# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
import os
import subprocess
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# 设置Chrome选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920x1080")

# 应用URL和端口
APP_URL = "http://127.0.0.1:5000"
APP_PORT = 5000

# Flask应用进程
FLASK_PROCESS = None


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """启动和停止Flask应用"""
    global FLASK_PROCESS
    
    # 启动Flask应用
    FLASK_PROCESS = subprocess.Popen([
        sys.executable, "app.py", "-e", "test"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd(), text=True)
    
    # 等待应用启动
    time.sleep(5)
    
    # 检查应用是否成功启动
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", APP_PORT))
        if result != 0:
            print("\n\nFlask应用没有成功启动！端口检查失败\n\n")
            # 打印Flask应用的输出
            stdout, stderr = FLASK_PROCESS.communicate(timeout=2)
            print(f"Flask应用stdout: {stdout}")
            print(f"Flask应用stderr: {stderr}")
        else:
            print("\n\nFlask应用成功启动！\n\n")
        sock.close()
    except Exception as e:
        print(f"检查Flask应用状态时出错: {e}")
    
    yield
    
    # 停止Flask应用
    if FLASK_PROCESS:
        FLASK_PROCESS.terminate()
        try:
            FLASK_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            FLASK_PROCESS.kill()


@pytest.fixture
def driver():
    """创建WebDriver实例"""
    # 初始化WebDriver
    from selenium.webdriver.chrome.service import Service
    service = Service()  # 使用PATH中的chromedriver.exe
    web_driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置隐式等待
    web_driver.implicitly_wait(5)
    
    yield web_driver
    
    # 关闭浏览器
    web_driver.quit()


class BaseTodoListTest:
    """基础TodoList测试类，提供通用方法"""
    
    def _clear_all_todos(self, _webdriver, wait):
        """清空所有待办事项"""
        try:
            # 直接使用JavaScript清空所有待办事项，避免StaleElementReferenceException
            _webdriver.execute_script(
                "window.confirm = function() { return true; }; ")
            # 先检查是否有批量删除功能
            try:
                # 检查select-all元素是否存在
                select_all_button = _webdriver.find_element(By.ID, "select-all")
                if select_all_button.is_displayed():
                    # 点击全选按钮
                    _webdriver.execute_script(
                        "arguments[0].click();", select_all_button)
                    # 点击删除选中按钮
                    delete_selected_button = _webdriver.find_element(
                        By.ID, "delete-selected")
                    _webdriver.execute_script(
                        "arguments[0].click();", delete_selected_button)
                    # 等待页面更新
                    time.sleep(1)
                    _webdriver.refresh()
                    return
            except Exception as e:
                print(f"批量删除失败: {e}")
                # 如果批量删除失败，尝试单个删除
            # 单个删除
            for _ in range(10):  # 最多尝试10次
                delete_buttons = _webdriver.find_elements(
                    By.CLASS_NAME, "btn-delete")
                # 过滤掉批量删除按钮
                individual_delete_buttons = [
                    button for button in delete_buttons 
                    if button.get_attribute("id") != "delete-selected"]
                if not individual_delete_buttons:
                    break
                for button in individual_delete_buttons:
                    try:
                        _webdriver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"删除单个待办事项时出错 {e}")
                        continue
                _webdriver.refresh()
                wait.until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "add-form")))
        except Exception as e:
            print(f"清空待办事项时出错 {e}")
            import traceback
            traceback.print_exc()

    def _add_todo(self, _webdriver, wait, title):
        """添加一个待办事项"""
        # 每次添加前都重新查找输入框，避免StaleElementReferenceException
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        # 先使用clear方法清除输入框，再使用JavaScript确保清除干净
        try:
            input_field.clear()
        except Exception as e:
            print(f"清除输入框失败，使用JavaScript清除: {e}")
        # 使用JavaScript清除输入框，确保清除干净
        _webdriver.execute_script("arguments[0].value = '';", input_field)
        # 重新获取add_button，确保它也是新鲜的
        add_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".add-form button")))
        input_field.send_keys(title)
        add_button.click()
        # 等待待办事项显示
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "todo-item")))

    def _add_recurring_todo(self, _webdriver, wait, title):
        """添加一个周期事项"""
        # 找到并点击周期切换复选框
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        # 等待周期设置显示
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "recurrence-settings")))
        # 添加待办事项
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        add_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".add-form button")))
        input_field.clear()
        input_field.send_keys(title)
        add_button.click()
        # 等待待办事项显示
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "todo-item")))