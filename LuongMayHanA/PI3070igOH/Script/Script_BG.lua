Script_BG_limits = 11

function we_bg_init()
    timer.create(0, 1, 1000, bg_ready_check)
end

function we_bg_poll()
    
end

function bg_ready_check()
    local ready = we_bas_getbit("@B_1#Application.M.hmi.plc_ready")
    if ready == 1 then
        we_bas_setbit("@B_1#Application.M.hmi.hmi_ready", 1)
    end
end