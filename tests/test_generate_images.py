#!/usr/bin/env python3
"""
Tests for generate_images.py — image generation logic
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../publishers/douyin-publisher/scripts"))

import generate_images as gi


class TestGetChineseFont:
    def test_returns_font_object(self):
        font = gi.get_chinese_font(36)
        assert font is not None

    def test_different_sizes(self):
        for size in [24, 36, 48, 72]:
            font = gi.get_chinese_font(size)
            assert font is not None


class TestGenerateCard:
    def test_creates_file(self, tmp_path):
        out = str(tmp_path / "test_card.jpg")
        result = gi.generate_card(
            output_path=out,
            title="测试标题",
            subtitle="副标题",
            body_lines=["要点一", "要点二"],
        )
        assert result == out
        assert os.path.isfile(out)
        assert os.path.getsize(out) > 0

    def test_creates_parent_dirs(self, tmp_path):
        out = str(tmp_path / "nested" / "deep" / "card.jpg")
        gi.generate_card(output_path=out, title="嵌套目录测试")
        assert os.path.isfile(out)

    def test_custom_colors(self, tmp_path):
        out = str(tmp_path / "color_card.jpg")
        gi.generate_card(
            output_path=out,
            title="颜色测试",
            bg_color=(50, 50, 50),
            accent_color=(255, 100, 0),
        )
        assert os.path.isfile(out)

    def test_with_brand_text(self, tmp_path):
        out = str(tmp_path / "brand_card.jpg")
        gi.generate_card(
            output_path=out,
            title="品牌测试",
            brand_text="我的品牌",
        )
        assert os.path.isfile(out)

    def test_body_lines_with_section_headers(self, tmp_path):
        out = str(tmp_path / "section_card.jpg")
        gi.generate_card(
            output_path=out,
            title="章节测试",
            body_lines=["## 章节一", "内容行", "---", "## 章节二", "更多内容"],
        )
        assert os.path.isfile(out)

    def test_no_body_lines(self, tmp_path):
        out = str(tmp_path / "empty_body.jpg")
        gi.generate_card(output_path=out, title="无正文")
        assert os.path.isfile(out)


class TestGenerateCards:
    def test_generates_default_count(self, tmp_path):
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="多图测试",
            points=["要点一", "要点二", "要点三"],
        )
        assert len(paths) == 3
        for p in paths:
            assert os.path.isfile(p)

    def test_generates_custom_count(self, tmp_path):
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="自定义数量",
            count=5,
            points=["A", "B", "C", "D", "E"],
        )
        assert len(paths) == 5

    def test_generates_one_card(self, tmp_path):
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="单张",
            count=1,
        )
        assert len(paths) == 1

    def test_default_points_when_none(self, tmp_path):
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="默认要点",
            points=None,
        )
        assert len(paths) == 3

    def test_fewer_points_than_count(self, tmp_path):
        """当 points 数量少于 count 时，应复用最后一个 point"""
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="要点不足",
            points=["只有一个要点"],
            count=3,
        )
        assert len(paths) == 3

    def test_output_filenames(self, tmp_path):
        paths = gi.generate_cards(output_dir=str(tmp_path), title="文件名测试", count=2)
        basenames = [os.path.basename(p) for p in paths]
        assert "card_1.jpg" in basenames
        assert "card_2.jpg" in basenames

    def test_with_subtitle(self, tmp_path):
        paths = gi.generate_cards(
            output_dir=str(tmp_path),
            title="副标题测试",
            subtitle="这是副标题",
            count=2,
        )
        assert len(paths) == 2


class TestDrawTextWrapped:
    def test_wraps_long_text(self, tmp_path):
        """长文本应自动换行，不抛出异常"""
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (1080, 1080), (20, 30, 60))
        draw = ImageDraw.Draw(img)
        font = gi.get_chinese_font(48)
        long_text = "这是一段非常非常非常非常非常非常非常非常非常非常非常非常长的测试文字用于验证自动换行功能"
        final_y = gi.draw_text_wrapped(draw, long_text, 100, font, "white")
        assert final_y > 100  # y 坐标应该增加了
