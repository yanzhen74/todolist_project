# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import APP_URL, BaseTodoListTest


class TestDeadlineFeatures(BaseTodoListTest):
    """截止日期功能测试"""

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_add_todo_with_deadline(self, driver):
        """测试添加带有截止日期的待办事项"""
        # 访问应用
        driver.get(APP_URL)
        
        # 添加待办事项
        input_field = driver.find_element(By.NAME, "title")
        #deadline_input = driver.find_element(By.NAME, "deadline")
        add_button = driver.find_element(By.CSS_SELECTOR, ".add-form button")
        
        todo_text = "Test todo with deadline"
        input_field.send_keys(todo_text)
        
        # 使用JavaScript直接设置截止日期值，避免格式化问题
        driver.execute_script(
            "document.getElementById('deadline').value = new Date(Date.now()"
            " + 24*60*60*1000).toISOString().slice(0, 16);")
        
        add_button.click()
        
        # 等待待办事项显示，使用显式等待代替固定等待时间
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素都是新鲜的
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 验证待办事项已添加
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        assert len(todo_items) > 0, "没有找到待办事项"
        
        # 查找包含指定文本的待办事项
        found_todo = False
        for item in todo_items:
            try:
                item_text = item.get_attribute("textContent")
                if todo_text in item_text:
                    found_todo = True
                    break
            except Exception:
                # 如果元素已过期，跳过
                continue
        assert found_todo, f"没有找到包含文本 '{todo_text}' 的待办事项"
        
        # 验证截止日期已显示
        deadline_elements = driver.find_elements(By.CLASS_NAME, "todo-deadline")
        assert len(deadline_elements) > 0, "没有找到截止日期元素"
        
        # 检查是否有可见的截止日期元素
        has_visible_deadline = False
        for element in deadline_elements:
            try:
                if element.is_displayed():
                    has_visible_deadline = True
                    break
            except Exception:
                # 如果元素已过期，跳过
                continue
        assert has_visible_deadline, "没有可见的截止日期元素"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_deadline_default_value(self, driver):
        """测试截止日期的默认值是否为当前时间+24小时"""
        # 访问应用
        driver.get(APP_URL)
        
        # 获取当前时间和默认截止时间
        current_time = driver.execute_script("return new Date().getTime();")
        default_deadline = driver.find_element(By.NAME, "deadline").get_attribute("value")
        
        # 将默认截止时间转换为时间戳
        default_deadline_time = driver.execute_script(
            f"return new Date('{default_deadline}').getTime();")
        
        # 计算时间差（毫秒）
        time_diff = default_deadline_time - current_time
        
        # 验证默认截止时间是否约为当前时间+24小时（允许1分钟误差）
        expected_diff = 24 * 60 * 60 * 1000  # 24小时
        tolerance = 60 * 1000  # 1分钟
        assert abs(time_diff - expected_diff) <= tolerance, \
        f"默认截止时间不正确，时间差：{time_diff/1000/60/60:.2f}小时"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_deadline_status_display(self, driver):
        """测试截止日期状态显示是否正确"""
        # 访问应用
        driver.get(APP_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # 首先清空所有现有待办事项
        try:
            delete_buttons = driver.find_elements(By.CLASS_NAME, "btn-delete")
            for button in delete_buttons:
                driver.execute_script("window.confirm = function() { return true; };")
                button.click()
                wait.until(EC.staleness_of(button))
        except Exception:
            pass
        
        # 刷新页面确保所有元素都是新鲜的
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 添加过期的待办事项
        input_field = wait.until(EC.presence_of_element_located((By.NAME, "title")))
        input_field.send_keys("Overdue todo")
        
        # 使用JavaScript直接设置过期日期
        driver.execute_script(
            "document.getElementById('deadline').value = "
            "new Date(Date.now() - 24*60*60*1000).toISOString().slice(0, 16);")
        
        add_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".add-form button")))
        add_button.click()
        
        # 等待添加完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素都是新鲜的
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 添加正常的待办事项
        input_field = wait.until(EC.presence_of_element_located((By.NAME, "title")))
        
        # 使用JavaScript清除输入框，避免StaleElementReferenceException
        driver.execute_script("document.querySelector('input[name=title]').value = '';")
        input_field.send_keys("Normal todo")
        
        # 使用JavaScript直接设置正常日期（5天后）
        driver.execute_script(
            "document.getElementById('deadline').value = new Date(Date.now() "
            "+ 5*24*60*60*1000).toISOString().slice(0, 16);")
        
        add_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".add-form button")))
        add_button.click()
        
        # 等待待办事项显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面以触发JavaScript状态更新
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 等待JavaScript执行完成，确保状态已更新
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # 再等1秒确保JavaScript状态更新完成
        time.sleep(1)
        
        # 获取所有截止日期元素
        deadline_elements = driver.find_elements(By.CLASS_NAME, "todo-deadline")
        assert len(deadline_elements) >= 2, f"预期至少2个截止日期元素，但实际有{len(deadline_elements)}个"
        
        # 查找过期和正常状态的元素
        has_overdue = False
        has_other = False
        for element in deadline_elements:
            try:
                element_class = element.get_attribute("class")
                if "overdue" in element_class:
                    has_overdue = True
                else:
                    has_other = True
            except Exception as e:
                print(f"处理元素时出错 {e}")
                # 如果元素已过期，跳过
                continue
        
        # 验证状态显示
        assert has_overdue, "没有找到过期状态的待办事项"
        assert has_other, "没有找到其他状态的待办事项"
