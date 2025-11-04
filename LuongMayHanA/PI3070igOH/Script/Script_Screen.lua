Script_Screen_limits = 11

local jump = false

function we_scr_init_0()

end

function we_scr_poll_0()
    local ready = we_bas_getbit("@B_1#Application.M.hmi.plc_ready")
    if ready == 1 and not jump then
        we_bas_jumpscreen(1)
        jump = true
    end
end

function we_scr_close_0()

end