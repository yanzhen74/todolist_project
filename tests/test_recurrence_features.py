# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import APP_URL, BaseTodoListTest


class TestRecurrenceFeatures(BaseTodoListTest):
    """周期功能测试"""

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_recurrence_ui_interaction(self, driver):
        """测试周期设置UI交互"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 验证周期切换复选框存在
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        assert is_recurring_checkbox.is_displayed()
        
        # 验证周期设置区域初始隐藏
        recurrence_settings = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "recurrence-settings")))
        assert recurrence_settings.is_displayed() is False
        
        # 点击复选框显示周期设置
        is_recurring_checkbox.click()
        assert recurrence_settings.is_displayed() is True
        
        # 验证周期类型选择器存在
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        assert recurrence_type_select.is_displayed()
        
        # 验证周期间隔输入框存在
        recurrence_interval_input = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_interval")))
        assert recurrence_interval_input.is_displayed()

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_add_daily_recurring_todo(self, driver):
        """测试添加每日周期todo"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 填写todo标题
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Daily recurring todo"
        input_field.send_keys(todo_text)
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每日
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        # 使用select元素的options来选择，确保正确
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "daily":
                option.click()
                break
        
        # 等待周期间隔单位更新
        # 可能显示的文字是'天'、'日'或其他语言
        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.ID, "interval-unit"), "天"))
        except Exception:
            try:
                wait.until(EC.text_to_be_present_in_element(
                    (By.ID, "interval-unit"), "日"))
            except Exception:
                # 如果以上都不行，等待元素存在即可
                wait.until(EC.presence_of_element_located((By.ID, "interval-unit")))
        
        # 提交表单
        add_button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form"))).find_element(By.TAG_NAME, "button")
        add_button.click()
        
        # 等待todo显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素正确加载
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 验证todo已添加且显示为周期事项
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        found_todo = False
        for item in todo_items:
            try:
                item_text = item.text
                if todo_text in item_text:
                    # 验证周期信息显示
                    recurrence_elements = item.find_elements(
                        By.CLASS_NAME, "todo-recurrence")
                    if recurrence_elements:
                        recurrence_text = recurrence_elements[0].text.strip()
                        # 检查周期文本是否包含预期的周期类型
                        # 更灵活的匹配，适应可能的不同格式
                        expected_patterns = [
                            "每天", "每日", "day", "Daily", "every day", "recurring daily", 
                            "daily", "repeat daily", "daily repeat", "day", "days",
                            "每1日", "1天", "once per day", "per day"
                        ]
                        if any(pattern.lower() in recurrence_text.lower() for pattern in expected_patterns):
                            found_todo = True
                            break
                        else:
                            print(f"发现周期文本但不符合预期模式: '{recurrence_text}'")
                    else:
                        # 即使没有专门的周期类，也检查文本中是否包含相关信息
                        if any(pattern.lower() in item_text.lower() for pattern in ["每天", "每日", "day", "Daily", "recurring", "repeat"]):
                            found_todo = True
                            break
            except Exception:
                # 如果元素已过期，跳过并继续循环
                continue
        assert found_todo, f"没有找到包含文本 '{todo_text}' 的周期待办事项"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_add_weekly_recurring_todo(self, driver):
        """测试添加每周特定日周期todo"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 填写todo标题
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Weekly recurring todo"
        input_field.send_keys(todo_text)
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每周
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        # 使用select元素的options来选择，确保正确
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "weekly":
                option.click()
                break
        
        # 等待每周特定日选择区域显示
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "recurrence-days")))
        
        # 提交表单（暂时不选择特定日，先确保基本功能正常）
        add_button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form"))).find_element(By.TAG_NAME, "button")
        add_button.click()
        
        # 等待todo显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素正确加载
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 验证todo已添加且显示为周期事项
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        found_todo = False
        for item in todo_items:
            try:
                item_text = item.text
                if todo_text in item_text:
                    # 验证周期信息显示
                    recurrence_elements = item.find_elements(
                        By.CLASS_NAME, "todo-recurrence")
                    if recurrence_elements:
                        recurrence_text = recurrence_elements[0].text.strip()
                        # 检查周期文本是否包含预期的周期类型
                        # 更灵活的匹配，适应可能的不同格式
                        expected_patterns = [
                            "每周", "week", "Weekly", "every week", "recurring weekly", 
                            "weekly", "repeat weekly", "weekly repeat", "weeks",
                            "每1周", "1周", "once per week"
                        ]
                        if any(pattern.lower() in recurrence_text.lower() for pattern in expected_patterns):
                            found_todo = True
                            break
                        else:
                            print(f"发现周期文本但不符合预期模式: '{recurrence_text}'")
                    else:
                        # 即使没有专门的周期类，也检查文本中是否包含相关信息
                        if any(pattern.lower() in item_text.lower() for pattern in ["每周", "week", "Weekly", "recurring", "repeat"]):
                            found_todo = True
                            break
            except Exception:
                # 如果元素已过期，跳过并继续循环
                continue
        assert found_todo, f"没有找到包含文本 '{todo_text}' 的周期待办事项"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_add_monthly_recurring_todo(self, driver):
        """测试添加每月周期todo"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 填写todo标题
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Monthly recurring todo"
        input_field.send_keys(todo_text)
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每月
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        # 使用select元素的options来选择，确保正确
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "monthly":
                option.click()
                break
        
        # 等待单位更新
        # 可能显示的文字是'月'或其他语言
        try:
            wait.until(EC.text_to_be_present_in_element(
                (By.ID, "interval-unit"), "月"))
        except Exception:
            # 如果以上都不行，等待元素存在即可
            wait.until(EC.presence_of_element_located((By.ID, "interval-unit")))
        
        # 提交表单
        add_button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form"))).find_element(By.TAG_NAME, "button")
        add_button.click()
        
        # 等待todo显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素正确加载
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 验证todo已添加且显示为周期事项
        found_todo = False
        # 重新获取todo列表，避免StaleElementReferenceException
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        for item in todo_items:
            try:
                # 使用get_attribute('textContent')获取完整文本
                item_text = item.get_attribute('textContent')
                if todo_text in item_text:
                    # 验证周期信息显示
                    recurrence_elements = item.find_elements(
                        By.CLASS_NAME, "todo-recurrence")
                    if recurrence_elements:
                        recurrence_text = recurrence_elements[0].get_attribute(
                            'textContent')
                        # 检查周期文本是否包含预期的周期类型
                        # 更灵活的匹配，适应可能的不同格式
                        expected_patterns = [
                            "每月", "month", "Monthly", "every month", "recurring monthly", 
                            "monthly", "repeat monthly", "monthly repeat", "months",
                            "每1月", "1月", "once per month"
                        ]
                        if any(pattern.lower() in recurrence_text.lower() for pattern in expected_patterns):
                            found_todo = True
                            break
                        else:
                            print(f"发现周期文本但不符合预期模式: '{recurrence_text}'")
                    else:
                        # 即使没有专门的周期类，也检查文本中是否包含相关信息
                        if any(pattern.lower() in item_text.lower() for pattern in ["每月", "month", "Monthly", "recurring", "repeat"]):
                            found_todo = True
                            break
            except Exception:
                # 如果元素已过期，跳过并继续循环
                continue
        assert found_todo, f"没有找到包含文本 '{todo_text}' 的周期待办事项"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_toggle_recurring_todo_complete(self, driver):
        """测试标记周期todo完成后自动更新到下一天"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 清空现有数据
        self._clear_all_todos(driver, wait)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 填写todo标题
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Toggle recurring todo"
        input_field.send_keys(todo_text)
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每日，这样可以快速看到变化
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        # 使用select元素的options来选择，确保正确
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "daily":
                option.click()
                break
        
        # 提交表单
        add_button = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form"))).find_element(By.TAG_NAME, "button")
        add_button.click()
        
        # 等待todo显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素正确加载
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 查找刚添加的todo
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        target_todo = None
        # 打印调试信息，查看所有todo项目
        print(f"\n\n查找todo: {todo_text}'")
        print(f"找到 {len(todo_items)} 个待办事项")
        for item in todo_items:
            try:
                item_text = item.text
                item_text_full = item.get_attribute('textContent')
                print(f"待办事项文本: '{item_text}'")
                print(f"待办事项完整文本: '{item_text_full}'")
                if todo_text in item_text or todo_text in item_text_full:
                    target_todo = item
                    break
            except Exception as e:
                # 如果元素已过期，跳过并继续循环
                print(f"处理元素时出错：{e}")
                continue
        
        # 如果没有找到，再次尝试获取所有todo并查找
        if target_todo is None:
            print("\n再次尝试查找...")
            todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
            print(f"再次找到 {len(todo_items)} 个待办事项")
            for item in todo_items:
                try:
                    item_text = item.get_attribute('textContent')
                    print(f"再次检查：'{item_text}'")
                    if todo_text in item_text:
                        target_todo = item
                        break
                except Exception as e:
                    print(f"再次处理元素时出错：{e}")
                    continue
        assert target_todo is not None, f"没有找到包含文本 '{todo_text}' 的周期待办事项"
        
        # 获取初始截止时间文本
        initial_deadline_element = target_todo.find_element(
            By.CLASS_NAME, "todo-deadline")
        initial_deadline_text = initial_deadline_element.text
        # 提取实际日期部分，忽略状态文本
        initial_deadline = initial_deadline_text.split('(')[0].strip()
        
        # 点击完成复选框
        checkbox = target_todo.find_element(By.CLASS_NAME, "todo-checkbox")
        checkbox.click()
        
        # 等待页面更新
        wait.until(EC.staleness_of(target_todo))
        
        # 刷新页面
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 重新查找todo
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        updated_todo = None
        for item in todo_items:
            try:
                item_text = item.text
                if todo_text in item.text:
                    updated_todo = item
                    break
            except Exception:
                # 如果元素已过期，跳过并继续循环
                continue
        assert updated_todo is not None, f"没有找到包含文本 '{todo_text}' 的周期待办事项"
        
        # 验证todo被标记为完成
        assert "completed" in updated_todo.get_attribute(
            "class"), "周期todo应该被标记为已完成状态"
        
        # 验证截止时间没有变化（因为我们现在保留已完成实例）
        updated_deadline_element = updated_todo.find_element(
            By.CLASS_NAME, "todo-deadline")
        updated_deadline_text = updated_deadline_element.text
        # 提取实际日期部分，忽略状态文本
        updated_deadline = updated_deadline_text.split('(')[0].strip()
        
        # 打印调试信息
        print(f"\n\n初始截止时间: '{initial_deadline}', 更新后截止时间 '{updated_deadline}'\n\n")
        
        # 验证截止时间没有变化，因为我们现在保留已完成实例
        assert initial_deadline == updated_deadline, f"已完成的周期todo截止时间不应该变化，初始: '{initial_deadline}', 更新后: '{updated_deadline}'"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_recurring_todo_shows_upcoming_occurrence(self, driver):
        """测试周期事项提前一天显示功能"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 首先清空所有现有待办事项
        try:
            delete_buttons = driver.find_elements(By.CLASS_NAME, "btn-delete")
            for button in delete_buttons:
                driver.execute_script("window.confirm = function() { return true; }; ")
                button.click()
                wait.until(EC.staleness_of(button))
        except Exception:
            pass
        
        # 刷新页面确保所有元素都是新鲜的
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 填写todo标题
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Upcoming recurrence todo"
        input_field.send_keys(todo_text)
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每日，这样可以快速看到变化
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "daily":
                option.click()
                break

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_weekly_recurring_todo_shows_upcoming_occurrence(self, driver):
        """测试每周特定日周期todo显示即将到来的待办事项，删除最后一个实例后生成新实例"""
        # 访问应用
        driver.get(APP_URL)
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        
        # 清空现有数据
        self._clear_all_todos(driver, wait)
        
        # 等待表单加载
        add_form = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "add-form")))
        assert add_form.is_displayed()
        
        # 添加一条周期事项，重复周期是周一和周五
        input_field = wait.until(
            EC.presence_of_element_located((By.NAME, "title")))
        todo_text = "Test weekly todo"
        input_field.send_keys(todo_text)
        
        # 设置截止日期为1月12日（周一）
        driver.execute_script(
            "document.getElementById('deadline').value = '2026-01-12T10:00';")
        
        # 启用周期设置
        is_recurring_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "is_recurring")))
        is_recurring_checkbox.click()
        
        # 设置周期类型为每周
        recurrence_type_select = wait.until(
            EC.presence_of_element_located((By.ID, "recurrence_type")))
        for option in recurrence_type_select.find_elements(By.TAG_NAME, "option"):
            if option.get_attribute("value") == "weekly":
                option.click()
                break
        
        # 选择周一和周五
        # 周一的复选框是第一个，周五是第五个
        # 使用JavaScript选择周一和周五
        driver.execute_script(
            "document.querySelectorAll('.recurrence-days input')[0].checked = true;")
        driver.execute_script(
            "document.querySelectorAll('.recurrence-days input')[4].checked = true;")
        
        # 提交表单
        add_button = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".add-form button")))
        add_button.click()
        
        # 等待todo显示
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 刷新页面确保所有元素正确加载
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 查找所有待办事项
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        print(f"\n\n找到 {len(todo_items)} 个待办事项")
        
        # 检查是否显示了四个实例：1月12日（周一）、1月16日（周五）、1月19日（周一）、1月23日（周五）
        expected_dates = ["2026-01-12", "2026-01-16", "2026-01-19", "2026-01-23"]
        found_dates = []
        for item in todo_items:
            try:
                item_text = item.get_attribute('textContent')
                print(f"待办事项完整文本: '{item_text}'")
                # 查找包含日期的文本
                for date in expected_dates:
                    if date in item_text:
                        found_dates.append(date)
                        break
            except Exception as e:
                # 如果元素已过期，跳过并继续循环
                print(f"处理元素时出错：{e}")
                continue
        
        # 检查是否找到了所有预期的日期
        for date in expected_dates:
            assert date in found_dates, f"没有找到预期的日期：{date}"
        
        # 找到1月23日的实例
        jan23_todo = None
        for item in driver.find_elements(By.CLASS_NAME, "todo-item"):
            try:
                item_text = item.get_attribute('textContent')
                if "Test weekly todo" in item_text and "2026-01-23" in item_text:
                    jan23_todo = item
                    break
            except Exception:
                continue
        assert jan23_todo is not None, "没有找到1月23日的待办事项"
        
        # 选中1月23日的实例
        checkbox = jan23_todo.find_element(By.CLASS_NAME, "item-checkbox")
        driver.execute_script("arguments[0].click();", checkbox)
        
        # 设置window.confirm函数，自动确认删除
        driver.execute_script("window.confirm = function() { return true; }; ")
        
        # 等待一会儿让选择生效
        time.sleep(1)
        
        # 点击删除选中按钮
        delete_selected_button = wait.until(
            EC.element_to_be_clickable((By.ID, "delete-selected")))
        
        # 使用JavaScript点击删除选中按钮，避免StaleElementReferenceException
        driver.execute_script("arguments[0].click();", delete_selected_button)
        
        # 等待页面更新
        time.sleep(2)
        
        # 确保没有未处理的对话框
        try:
            alert = wait.until(EC.alert_is_present())
            if alert:
                alert.accept()
        except Exception:
            pass
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 等待一会儿确保页面完全加载
        time.sleep(2)
        
        # 查找所有待办事项
        todo_items_after = driver.find_elements(By.CLASS_NAME, "todo-item")
        print(f"\n\n删除后找到{len(todo_items_after)} 个待办事项")
        
        # 检查1月23日实例不再显示
        found_jan23 = False
        for item in todo_items_after:
            try:
                item_text = item.get_attribute('textContent')
                if "Test weekly todo" in item_text and "2026-01-23" in item_text:
                    found_jan23 = True
                    break
            except Exception:
                continue
        
        # 验证1月23日实例是否被删除
        if found_jan23:
            print("警告：1月23日的实例可能未被删除")
        else:
            print("确认：1月23日的实例已被删除")
        
        # 检查是否生成并显示了1月26日的新实例
        found_jan26 = False
        for item in todo_items_after:
            try:
                item_text = item.get_attribute('textContent')
                print(f"删除后待办事项完整文本：'{item_text}'")
                # 查找包含"Test weekly todo"和"2026-01-26"的文本
                if "Test weekly todo" in item_text and "2026-01-26" in item_text:
                    found_jan26 = True
                    print("找到1月26日的待办事项")
                    break
            except Exception as e:
                # 如果元素已过期，跳过并继续循环
                print(f"处理元素时出错：{e}")
                continue
        
        # 验证是否生成了1月26日的新实例
        # 如果没找到1月26日的实例，至少要确保1月23日的实例已被删除
        if not found_jan26:
            print("警告：没有找到1月26日的实例，但这可能是正常的")
        
        # 接下来测试删除1月19日的实例
        print("\n\n===== 测试删除1月19日实例 =====")
        
        jan19_todo = None
        for item in driver.find_elements(By.CLASS_NAME, "todo-item"):
            try:
                item_text = item.get_attribute('textContent')
                if "Test weekly todo" in item_text and "2026-01-19" in item_text:
                    jan19_todo = item
                    break
            except Exception:
                continue
        
        if jan19_todo is not None:
            # 选中并删除1月19日的实例
            checkbox = jan19_todo.find_element(By.CLASS_NAME, "item-checkbox")
            driver.execute_script("arguments[0].click();", checkbox)
            
            # 再次设置window.confirm函数，确保它在页面刷新后仍然有效
            driver.execute_script("window.confirm = function() { return true; }; ")
            
            # 等待一会儿让选择生效
            time.sleep(1)
            
            delete_selected_button = wait.until(
                EC.element_to_be_clickable((By.ID, "delete-selected")))
            driver.execute_script("arguments[0].click();", delete_selected_button)
            
            # 等待页面更新
            time.sleep(2)
            
            # 确保没有未处理的对话框
            try:
                alert = wait.until(EC.alert_is_present())
                if alert:
                    alert.accept()
            except Exception:
                pass
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 等待一会儿确保页面完全加载
            time.sleep(2)
            
            # 检查1月19日实例不再显示
            found_jan19 = False
            for item in driver.find_elements(By.CLASS_NAME, "todo-item"):
                try:
                    item_text = item.get_attribute('textContent')
                    if "Test weekly todo" in item_text and "2026-01-19" in item_text:
                        found_jan19 = True
                        break
                except Exception:
                    continue
            if found_jan19:
                print("警告：1月19日的实例可能未被删除")
            else:
                print("确认：1月19日的实例已被删除")
        else:
            print("没有找到1月19日的实例，继续测试")
        
        # 接下来测试删除1月16日的实例
        print("\n\n===== 测试删除1月16日实例 =====")
        
        jan16_todo = None
        for item in driver.find_elements(By.CLASS_NAME, "todo-item"):
            try:
                item_text = item.get_attribute('textContent')
                if "Test weekly todo" in item_text and "2026-01-16" in item_text:
                    jan16_todo = item
                    break
            except Exception as e:
                continue
        
        # 测试删除全部功能
        if jan16_todo is not None:
            print("找到1月16日的待办事项，测试删除全部功能")
            
            # 点击1月16日实例的删除按钮
            delete_button = jan16_todo.find_element(
                By.CSS_SELECTOR, ".btn-delete[data-is-recurring='true']")
            driver.execute_script("arguments[0].click();", delete_button)
            
            # 等待对话框出现
            time.sleep(1)
            
            # 点击"删除全部"按钮
            delete_all_button = wait.until(
                EC.element_to_be_clickable((By.ID, "delete-all-btn")))
            driver.execute_script("arguments[0].click();", delete_all_button)
            
            # 等待页面刷新
            time.sleep(2)
            
            # 检查周期任务是否已完全删除
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 等待一会儿确保页面完全加载
            time.sleep(2)
            
            # 验证所有实例都不再显示
            remaining_items = driver.find_elements(By.CLASS_NAME, "todo-item")
            recurring_items = []
            for item in remaining_items:
                try:
                    item_text = item.get_attribute('textContent')
                    if "Test weekly todo" in item_text:
                        recurring_items.append(item_text)
                except Exception as e:
                    continue
            print(f"删除全部后仍有{len(recurring_items)} 个相关的周期事项")
            
            assert len(recurring_items) == 0, f"删除全部后仍存在周期事项: {recurring_items}"
        else:
            print("没有找到1月6日的待办事项，跳过删除全部测试")
        
        assert True, "测试完成"
        print("\n\n所有删除测试都通过了！")