from playwright.sync_api import expect


def test_earth_article_no_incorrect_oxygen_value(page):
    """
    Тест проверяет, что в статье "Земля" на ru.wikipedia.org
    отсутствует неправильное значение содержания кислорода "50,00"
    """
    # Шаг 1: Открыть https://ru.wikipedia.org
    page.goto("https://ru.wikipedia.org")
    
    # Шаг 2: Ввести в строку поиска "Земля"
    search_input = page.locator("#searchInput")
    search_input.fill("Земля")
    
    # Шаг 3: Перейти на статью "Земля" (нажать Enter или кликнуть на первую ссылку)
    search_input.press("Enter")
    
    # Ждем загрузки статьи
    page.wait_for_load_state("networkidle")
    
    # Проверяем, что мы на странице статьи "Земля" (заголовок содержит "Земля")
    title = page.title()
    assert "Земля" in title, f"Ожидалось, что заголовок содержит 'Земля', но получен: {title}"
    
    # Шаг 4: Проверить, что в статье НЕТ текста "50,00" (неправильное значение содержания кислорода)
    # Используем page.locator для поиска текста "50,00" на странице
    incorrect_value_locator = page.locator("text=50,00")
    
    # Проверяем используя expect, что элемент с текстом "50,00" не существует (count = 0)
    expect(incorrect_value_locator).to_have_count(0)
