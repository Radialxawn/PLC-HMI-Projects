Script_BG_limits = 11

local bg_id_bit = {
    plc_ready = "@B_1#Application.M.hmi.plc_ready",
    hmi_ready = "@B_1#Application.M.hmi.hmi_ready",
    save_need_check = "@B_1#Application.M.hmi.sv_need_check",
    pf_draw_repeat_debug = "@B_0#HDX200.0",
    pf_name_process_debug = "@B_0#HDX200.1",
    pf_name_update = "@B_1#Application.M.hmi.pf_name_update",
    pf_name_save_trigger = "@B_1#Application.M.hmi.pf_name_save_trigger",
}

local bg_id_name_show = function (index)
    return "@W_0#HDW"..index
end

local bg_repeat_count = {0, 0, 0, 0, 0}
local bg_repeat_end = function (id, max)
    bg_repeat_count[id] = bg_repeat_count[id] + 1
    if bg_repeat_count[id] >= max then
        bg_repeat_count[id] = 0
        return true
    end
    return false
end

function we_bg_init()
    timer.create(-1, 1, 1000, bg_ready_check)
    timer.create(-1, 2, 200, bg_set_save_need_repeat)
    timer.create(1, 3, 200, bg_pf_name_update_check)
    timer.create(1, 4, 200, bg_pf_name_update_repeat)
    timer.create(1, 5, 200, bg_pf_draw_repeat)
end

function we_bg_poll()
    
end

function bg_ready_check()
    local ready = we_bas_getbit(bg_id_bit.plc_ready)
    if ready == 1 then
        we_bas_setbit(bg_id_bit.hmi_ready, 1)
    end
end
-------------------------------------------------------------------------
-------------------------------------------------------------------------
function bg_popup_check_accept()
    we_bas_setint("@W_0#HUW1434", 1)
    timer.set_status(-1, 2, 1)
end

function bg_set_save_need_repeat()
    we_bas_setbit(bg_id_bit.save_need_check, 1)
    if bg_repeat_end(1, 2) == true then
        timer.set_status(-1, 2, 0)
    end
end

function bg_pf_name_update_check()
    local pf_name_update = we_bas_getbit(bg_id_bit.pf_name_update)
    if pf_name_update == 1 then
        we_bas_setbit(bg_id_bit.pf_name_update, 0)
        timer.set_status(1, 4, 1)
    end
end
-------------------------------------------------------------------------
-------------------------------------------------------------------------
local bg_id_pf_name = {
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
}

local bg_pf_name_update_in_progress = 0
function bg_pf_name_update()
    if bg_pf_name_update_in_progress == 1 then
        return false
    end
    bg_pf_name_update_in_progress = 1
    for i, v in ipairs(bg_id_pf_name) do
        local w = we_bas_getword(v)
        if w ~= nil then
            we_bas_setword(bg_id_name_show(i - 1), w)
        end
    end
    bg_pf_name_update_in_progress = 0
    return true
end

function bg_pf_name_update_repeat()
    we_bas_setbit(bg_id_bit.pf_name_process_debug, 1)
    if bg_pf_name_update() == true then
        if bg_repeat_end(2, 3) == true then
            we_bas_setbit(bg_id_bit.pf_name_process_debug, 0)
            timer.set_status(1, 4, 0)
        end
    end
end

function bg_pf_name_save()
    local save = we_bas_getbit(bg_id_bit.pf_name_save_trigger)
    if save == 1 then
        return
    end
    for i, v in ipairs(bg_id_pf_name) do
        local w = we_bas_getword(bg_id_name_show(i - 1))
        we_bas_setword(v, w)
    end
    we_bas_setbit(bg_id_bit.pf_name_save_trigger, 1)
end

function bg_pf_draw_repeat()
    we_bas_setbit(bg_id_bit.pf_draw_repeat_debug, 1)
    if draw_pf() == true then
        we_bas_setbit(bg_id_bit.pf_draw_repeat_debug, 0)
    end
end