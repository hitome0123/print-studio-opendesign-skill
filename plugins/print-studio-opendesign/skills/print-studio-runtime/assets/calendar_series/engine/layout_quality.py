"""Shared layout quality helpers.

These helpers are intentionally deterministic: they do not judge beauty with a
model, but encode reusable print-layout guardrails that apply across product
templates.
"""


def bbox_intersects(a, b, gap=0):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (ax1 + gap <= bx0 or bx1 + gap <= ax0 or ay1 + gap <= by0 or by1 + gap <= ay0)


def bbox_inside_safe(bbox, canvas, safe_px):
    x0, y0, x1, y1 = bbox
    width, height = canvas
    return x0 >= safe_px and y0 >= safe_px and width - x1 >= safe_px and height - y1 >= safe_px


def vertical_stack_start(preferred_y, stack_h, min_y, max_y):
    y = preferred_y
    if y + stack_h > max_y:
        y = max_y - stack_h
    if y < min_y:
        y = min_y
    return round(y)

