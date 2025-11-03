Script_Draw_limits = 11

function draw_curve_test()
    local style = {
        color = 0x000000,
        linetype = 0,
        width = 1,
        visible = 1,
    }
    local gridStyle = {
        color = 0xcccccc,
        linetype = 2,
        width = 1,
        visible = 1,
    }
    local line1Style = {
        color = 0x00868b,
        linetype = 0,
        width = 1,
        visible = 1,
    }
    local referStyle = {
        color = 0x00468b,
        linetype = 0,
        width = 1,
        visible = 1,
    }
    local cursorStyle = {
        color = 0xff0000,
        linetype = 2,
        width = 1,
        visible = 1,
    }
    local xy = {1, 3, 2, 1, 3, 4, 4, 1}
    local part = "0_CST_0"
    cus_curve.init(part, 3, 3)
    cus_curve.set_range(part, "x", 1, 4)
    cus_curve.set_range(part, "y", 1, 4)
    cus_curve.set_scale(part, "x", style)
    cus_curve.set_scale(part, "y", style)
    cus_curve.set_grid(part, "x", gridStyle)
    cus_curve.set_grid(part, "y", gridStyle)
    cus_curve.set_line(part, 1, 4, line1Style)
    -- cus_curve.set_visible(part, 1, 0)
    cus_curve.set_refer(part, "x", 1, 1.5, referStyle)
    cus_curve.set_cursor(part, 0, cursorStyle)
    cus_curve.draw_line(part, 1, xy)
    cus_curve.refresh(part)
    
    print(cus_curve.get_range(part, "x"))
    print(cus_curve.get_scale(part, "x"))
    print(cus_curve.get_grid(part, "x"))
    print(cus_curve.get_label(part, "x"))
    print(cus_curve.get_line(part, 1))
    print(cus_curve.get_visible(part, 1))
end