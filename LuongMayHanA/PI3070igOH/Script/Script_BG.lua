Script_BG_limits = 11

function we_bg_init()
    timer.create(-1, 1, 1000, bg_ready_check)
    timer.create(-1, 2, 100, bg_set_save_need_check)
    timer.create(1, 3, 100, bg_draw_check)
    timer.create(1, 4, 200, bg_profile_name_get)
end

function we_bg_poll()
    
end

function bg_ready_check()
    local ready = we_bas_getbit("@B_1#Application.M.hmi.plc_ready")
    if ready == 1 then
        we_bas_setbit("@B_1#Application.M.hmi.hmi_ready", 1)
    end
end
-------------------------------------------------------------------------
-------------------------------------------------------------------------
local bg_set_save_need_check_count = 0
function bg_popup_check_accept()
    we_bas_setint("@W_0#HUW1434", 1)
    timer.set_status(-1, 2, 1)
end

function bg_set_save_need_check()
    we_bas_setbit("@B_1#Application.M.hmi.sv_need_check", 1)
    bg_set_save_need_check_count = bg_set_save_need_check_count + 1
    if bg_set_save_need_check_count >= 3 then
        bg_set_save_need_check_count = 0
        timer.set_status(-1, 2, 0)
    end
end
-------------------------------------------------------------------------
-------------------------------------------------------------------------
function utf8_from(t)
    local bytearr = {}
    for _, v in ipairs(t) do
        local utf8byte = v < 0 and (0xff + v + 1) or v
        table.insert(bytearr, string.char(utf8byte))
    end
    return table.concat(bytearr)
end

local bg_profile_name_get_id = {
    "@W_1#Application.M.hmi.pf_name_as_array[0]",
    "@W_1#Application.M.hmi.pf_name_as_array[1]",
    "@W_1#Application.M.hmi.pf_name_as_array[2]",
    "@W_1#Application.M.hmi.pf_name_as_array[3]",
    "@W_1#Application.M.hmi.pf_name_as_array[4]",
    "@W_1#Application.M.hmi.pf_name_as_array[5]",
    "@W_1#Application.M.hmi.pf_name_as_array[6]",
    "@W_1#Application.M.hmi.pf_name_as_array[7]",
    "@W_1#Application.M.hmi.pf_name_as_array[8]",
    "@W_1#Application.M.hmi.pf_name_as_array[9]",
    "@W_1#Application.M.hmi.pf_name_as_array[10]",
    "@W_1#Application.M.hmi.pf_name_as_array[11]",
    "@W_1#Application.M.hmi.pf_name_as_array[12]",
    "@W_1#Application.M.hmi.pf_name_as_array[13]",
    "@W_1#Application.M.hmi.pf_name_as_array[14]",
    "@W_1#Application.M.hmi.pf_name_as_array[15]",
    "@W_1#Application.M.hmi.pf_name_as_array[16]",
    "@W_1#Application.M.hmi.pf_name_as_array[17]",
    "@W_1#Application.M.hmi.pf_name_as_array[18]",
    "@W_1#Application.M.hmi.pf_name_as_array[19]"
}

local bg_profile_name_get_count = 0
function bg_profile_name_get()
    local ws = {}
    for i = 1, 20 do
        local w = we_bas_getword(bg_profile_name_get_id[i])
        table.insert(ws, w)
    end
    we_bas_setstring("@W_0#HDW0", utf8_from(ws))
    bg_profile_name_get_count = bg_profile_name_get_count + 1
    if bg_profile_name_get_count >= 3 then
        bg_profile_name_get_count = 0
        timer.set_status(1, 4, 0)
    end
end
-------------------------------------------------------------------------
-------------------------------------------------------------------------
local bg_draw_ing = 0
function bg_draw_check()
    local draw = we_bas_getbit("@B_1#Application.M.hmi.pf_draw")
    if draw == 1 and bg_draw_ing == 0 then
        bg_draw_ing = 1
        draw_profile()
        we_bas_setbit("@B_1#Application.M.hmi.pf_draw", 0)
        bg_draw_ing = 0
        timer.set_status(1, 4, 1)
    end
end