import xml.etree.ElementTree as ET

import lxml.etree as etree
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/parse", methods=["POST"])
def parse_xml():
    """
    Уязвимый endpoint для парсинга XML
    Принимает XML и возвращает обработанные данные
    """
    try:
        xml_data = request.data

        if not xml_data:
            return jsonify({"error": "No XML data provided"}), 400

        # УЯЗВИМОСТЬ: Парсер настроен небезопасно!
        # resolve_entities=True позволяет обрабатывать внешние сущности
        parser = etree.XMLParser(resolve_entities=True, no_network=False)

        try:
            doc = etree.fromstring(xml_data, parser)
        except Exception as e:
            return jsonify({"error": f"XML parsing error: {str(e)}"}), 400

        # Извлекаем данные из XML
        result = {}
        result["message"] = "XML successfully parsed!"
        result["root_tag"] = doc.tag

        # Пытаемся извлечь текстовое содержимое
        if doc.text:
            result["content"] = doc.text.strip()

        # Обрабатываем дочерние элементы
        children = {}
        for child in doc:
            if child.text:
                children[child.tag] = child.text.strip()

        if children:
            result["elements"] = children

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/example")
def example():
    """
    Показывает пример валидного XML запроса
    """
    example_xml = """<?xml version="1.0" encoding="UTF-8"?>
<user>
    <name>John Doe</name>
    <email>john@example.com</email>
    <message>Hello, World!</message>
</user>"""

    return jsonify(
        {
            "example": example_xml,
            "hint": "Try sending this XML to /api/parse endpoint using POST method",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
