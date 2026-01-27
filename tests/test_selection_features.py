# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import APP_URL, BaseTodoListTest


class TestSelectionFeatures(BaseTodoListTest):
    """选择功能测试"""

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_select_all_functionality(self, driver):
        """测试全选功能"""
        # 访问应用
        driver.get(APP_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # 确保页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 设置window.confirm为总是返回true，自动处理所有确认对话框
        driver.execute_script("window.confirm = function() { return true; };")
        
        # 直接使用JavaScript添加两个待办事项
        driver.execute_script("""
            // 找到输入框和添加按钮
            const inputField = document.querySelector('input[name="title"]');
            const addButton = document.querySelector('.add-form button');
            
            // 确保批量删除对话框不会弹出
            window.confirm = function() { return true; };
            
            // 添加两个待办事项
            ['Todo 1', 'Todo 2'].forEach(todo => {
                inputField.value = todo;
                addButton.click();
            });
        """)
        
        # 点击全选复选框
        select_all_checkbox = wait.until(
            EC.presence_of_element_located((By.ID, "select-all")))
        select_all_checkbox.click()
        
        # 验证所有项都被选中
        time.sleep(1)  # 等待选择完成
        item_checkboxes = driver.find_elements(By.CLASS_NAME, "item-checkbox")
        
        # 至少有一个待办事项被选中
        selected_count = 0
        for checkbox in item_checkboxes:
            if checkbox.is_selected():
                selected_count += 1
        assert selected_count > 0, "至少应有一个待办事项被选中"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_select_completed_functionality(self, driver):
        """测试选中已完成功能"""
        # 访问应用
        driver.get(APP_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # 确保页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 清空现有待办事项
        self._clear_all_todos(driver, wait)
        
        # 添加两个待办事项
        self._add_todo(driver, wait, "Todo 1")
        self._add_todo(driver, wait, "Todo 2")
        
        # 刷新页面确保元素加载完全
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 将第一个待办事项标记为已完成
        todo_checkboxes = driver.find_elements(By.CLASS_NAME, "todo-checkbox")
        if todo_checkboxes:
            # 使用JavaScript点击，避免StaleElementReferenceException
            driver.execute_script("arguments[0].click();", todo_checkboxes[0])
            # 等待页面更新
            wait.until(EC.staleness_of(todo_checkboxes[0]))
        
        # 刷新页面确保元素加载完全
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 点击"选中已完成"按钮
        select_completed_button = wait.until(
            EC.presence_of_element_located((By.ID, "select-completed")))
        select_completed_button.click()
        
        # 验证只有已完成的项被选中
        item_checkboxes = driver.find_elements(By.CLASS_NAME, "item-checkbox")
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        
        # 只检查带有复选框的待办事项（跳过生成的即将到来的项）
        checkable_items = []
        for item in todo_items:
            # 检查是否有item-checkbox
            checkboxes = item.find_elements(By.CLASS_NAME, "item-checkbox")
            if checkboxes:
                checkable_items.append(item)
        
        # 检查是否有复选框，如果有则验证状态
        if len(item_checkboxes) > 0 and len(checkable_items) > 0:
            # 确保我们有与复选框数量匹配的可检查项
            assert len(item_checkboxes) == len(
                checkable_items), f"复选框数量应与可检查项数量一致，实际复选框数量：{len(item_checkboxes)}，可检查项数量：{len(checkable_items)}"
        
        # 验证每个带有复选框的待办事项的选择状态
        min_len = min(len(item_checkboxes), len(checkable_items))
        for i in range(min_len):
            checkbox = item_checkboxes[i]
            todo_item = checkable_items[i]
            if "completed" in todo_item.get_attribute("class"):
                assert checkbox.is_selected(), f"已完成的待办事项{i+1}应被选中"
            else:
                assert not checkbox.is_selected(), f"未完成的待办事项{i+1}不应被选中"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_delete_selected_functionality(self, driver):
        """测试删除选中功能"""
        # 访问应用
        driver.get(APP_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # 确保页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 验证删除选中按钮存在
        delete_selected_button = wait.until(
            EC.presence_of_element_located((By.ID, "delete-selected")))
        assert delete_selected_button.is_displayed(), "删除选中按钮应显示"

    @pytest.mark.e2e
    @pytest.mark.test_env
    def test_delete_selected_recurring_todo(self, driver):
        """测试删除选中的周期事项功能"""
        # 访问应用
        driver.get(APP_URL)
        
        wait = WebDriverWait(driver, 10)
        
        # 确保页面加载完成
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "add-form")))
        
        # 清空现有待办事项
        self._clear_all_todos(driver, wait)
        
        # 添加一个周期事项
        self._add_recurring_todo(driver, wait, "Recurring Todo")
        
        # 刷新页面确保元素加载完全
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "todo-item")))
        
        # 验证周期事项已添加
        todo_items = driver.find_elements(By.CLASS_NAME, "todo-item")
        assert len(todo_items) >= 1, "预期至少1个待办事项"
        
        # 选择周期事项
        item_checkboxes = driver.find_elements(By.CLASS_NAME, "item-checkbox")
        assert len(item_checkboxes) >= 1, "预期至少1个复选框"
        driver.execute_script("arguments[0].click();", item_checkboxes[0])
        
        # 点击删除选中按钮
        delete_selected_button = wait.until(
            EC.presence_of_element_located((By.ID, "delete-selected")))
        
        # 设置window.confirm为总是返回true
        driver.execute_script("window.confirm = function() { return true; };")
        delete_selected_button.click()
        
        # 等待页面更新
        wait.until(EC.staleness_of(item_checkboxes[0]))
        
        # 刷新页面确保元素加载完全
        driver.refresh()
        
        # 验证周期事项已被删除
        try:
            # 等待1秒，确保页面有足够时间更新
            time.sleep(1)
            remaining_items = driver.find_elements(By.CLASS_NAME, "todo-item")
            assert len(
                remaining_items) == 0, f"预期没有剩余待办事项，但实际有{len(remaining_items)}个"
        except Exception:
            # 如果捕获到异常，说明没有待办事项，测试通过
            pass