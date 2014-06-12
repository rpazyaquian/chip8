// Auxiliary functions

function randrange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function create_ram(size) {

    var ram_size = size;
    var ram = new Array(size);
    
    for (var i = 0; i<size; i++) {
    
        ram[i] = 0;
    
    }
    
    return ram;

}

function create_screen(height, width) {

    var screen_height = height;
    var screen_width = width;
    var screen = new Array(height);
    
    for (var i = 0; i<screen_width; i++) {
        screen[i] = new Array(64);
        for (var j = 0; j<screen_height; j++) {
            screen[i][j] = 0;
        }
    }
    
    return screen;
}

function create_sprite_array(height) {
    sprite_array = // finish me!
}

// Rendering functions

function draw_screen(screen, context) {

    for (var i = 0; i < screen.length; i++) {

        for (var j = 0; j < screen[i].length; j++) {

            var value = screen[i][j];
            
            if (value === 0) {
                context.fillStyle = '#000000';
                context.fillRect(i*tile_res, j*tile_res, tile_res, tile_res);
            } else {
                context.fillStyle = '#FFFFFF';
                context.fillRect(i*tile_res, j*tile_res, tile_res, tile_res);
            }
        }

    }

}

// Logic functions


function cls() {

    for (var i = 0; i < screen.length; i++) {
        for (var j = 0; j < screen[i].length; j++) {
            screen[i][j] = 0;
        }
    }

}

function ret() {

    sp -= 1;
    pc = stack[sp];

}

function jump(nnn) {

    pc = nnn;

}

function call(nnn) {

    stack[sp] = pc;
    sp++;
    pc = nnn;

}

function se_byte(x, nn) {

    if (v[x] === nn) {
        pc += 2;
    }

}

function sne_byte(x, nn) {
    if (v[x] !== nn) {
        pc += 2;
    }
}

function se_reg(x, y) {
    if (v[x] === v[y]) {
        pc += 2;
    }
}

function ld_byte(x, nn) {
    v[x] = nn;
}

function add_byte(x, nn){
    v[x] += nn;
    if (v[x] > 0xFF) {
        v[x] -= 0xFF;
    }
}

function ld_reg(x, y) {
    v[x] = v[y];
}

function or_reg(x, y) {
    v[x] = (v[x] | v[y]);
}

function and_reg(x, y) {
    v[x] = (v[x] & v[y]);
}

function xor_reg(x, y) {
    v[x] = (v[x] ^ v[y]);
}

function add_reg(x, y) {
    if ((v[x] + v[y]) > 0xFF) {
        v[15] = 1;
        v[x] += v[y];
        v[x] -= 0xFF;
    } else {
        v[15] = 0;
        v[x] += v[y];
    }
}

function sub_reg(x, y) {
    if (v[x] > v[y]) {
        v[15] = 1;
        v[x] -= v[y];
    } else {
        // eg: v[x] = 9, v[y] = 10
        v[15] = 0;
        v[x] -= v[y];  // 9 - 10 = -1
        v[x] = (v[x] & 0xFF); // -1 & 0xFF = 0xFF, 0 & 0xFF = 0, -2 & 0xFF = 0xFE, etc.
    }
}

function shr(x) {
    v[15] = (v[x] & 1);
    v[x] = (v[x] >> 1);
}

function subn(x, y) {
    if (v[y] > v[x]) {
        v[15] = 1;
        v[x] = (v[y] - v[x]);
    } else {
        // eg v[x] = 10, v[y] = 9
        v[15] = 0;
        v[x] = (v[y] - v[x]);  // v[x] = (9 - 10) = -1 - will give negative number
        v[x] = (v[x] & 0xFF); // -1 & 0xFF = 0xFF, 0 & 0xFF = 0, -2 & 0xFF = 0xFE, etc.
    }
}

function shl(x) {
    v[15] = (v[x] & 1);
    v[x] = (v[x] << 1);
}

function sne_reg(x, y) {
    if (v[x] != v[y]) {
        pc += 2;
    }
}

function ld_i(nnn) {
    i = nnn;
}

function jump_v0(nnn) {
    pc = (nnn + v[0]);
}

function rnd_reg(x, nn) {
    v[x] = (randrange(0, 255) & nn);
}

function draw(x, y, n) {
    // uhhhh
}



function command_to_opcode(command) {

    pc += 2;
   
    switch(command.a) {
    
        case 0:
            
            switch(command.insn) {
            
                case 224:
                    cls();
                    break;
                    
                case 238:
                    ret();
                    break;
                    
                default:
                    console.log("invalid opcode");
                    break;
            
            }
            
            break;
        
        case 1:
            
            jump(command.nnn);
            
            break;
        
        case 2:
            
            call(console.nnn);
            
            break;
        
        case 3:
            
            se_byte(command.x, command.nn);
            
            break;
        
        case 4:
            
            sne_byte(command.x, command.nn);
            
            break;
        
        case 5:
            
            se_reg(command.x, command.y);
            
            break;
        
        case 6:
            
            ld_byte(command.x, command.nn);
            
            break;
        
        case 7:
            
            add_byte(command.x, command.nn);
            
            break;
        
        case 8:
            
            switch(command.n) {
            
                case 0:
                    
                    ld_reg(command.x, command.y);
                    
                    break;
                case 1:
                    
                    or_reg(command.x, command.y);
                    
                    break;
                case 2:
                    
                    and_reg(command.x, command.y);
                    
                    break;
                case 3:
                    
                    xor_reg(command.x, command.y);
                    
                    break;
                case 4:
                    
                    add_reg(command.x, command.y);
                    
                    break;
                case 5:
                    
                    sub_reg(command.x, command.y);
                    
                    break;
                case 6:
                    
                    // shift right 1
                    shr(command.x);
                    
                    break;
                case 7:
                    
                    // set vx to (vx - vy)
                    subn(command.x, command.y);
                    
                    break;
                case 14:
                    
                    // shift left 1
                    shl(command.x);
                    
                    break;
            
            }
            
            break;
        
        case 9:
            
            sne_reg(command.x, command.y);
            
            break;
        
        case 10:
            
            ld_i(command.nnn);
            
            break;
        
        case 11:
            
            // jump to NNN + V0
            jump_v0(command.nnn)
            
            break;
        
        case 12:
            
            // set VX to (random number & NN)
            rnd_reg(command.x, command.nn);
            
            break;
        
        case 13:
            
            draw(command.x, command.y, command.n);
            
            break;
        
        case 14:
            
            switch(command.nn) {
            
                case 158:
                    
                    skp(command.x);
                    
                    break;
                case 161:
                    
                    sknp(command.x);
                    
                    break;
                default:
                    console.log('invalid opcode');
                    break;
            
            
            }
            
            break;
        
        case 15:
            
            switch(command.nn) {

                case 7:

                    ld_delay(command.x);
                    break;

                case 10:

                    ld_key(command.x);
                    break;

                case 21:

                    set_delay(command.x);
                    break;

                case 24:

                    set_sound(command.x);
                    break;

                case 30:

                    // set i to (i + vx)
                    add_i(command.x);
                    break;

                case 41:

                    // set i to location of sprite for character X. (e.g. 0, 1, E, F)
                    i_font(command.x);

                    break;

                case 51:

                    // store binary-coded decimal rep of VX, hundreds digit @ I, tens digit @ I+1, ones digit @ I+2
                    bin(command.x); 

                    break;

                case 85:

                    // store v0 to vx in memory starting at I
                    mem_save(command.x);

                    break;

                case 101:

                    // fill v0 to vx with values from memory starting at I
                    mem_load(command.x)

                    break;

            }
            
            break;
        
        default:
            console.log('invalid opcode');
    
    }
}

// Bitshift functions

function shortify(lbyte, rbyte) {

    return (lbyte << 8 | rbyte);

}

function short_to_command(byte_pair) {
    
    // takes output from shortify();
    
    var command = {};

    command.insn = byte_pair; 
    command.nnn = byte_pair & 0x0FFF;  // get last three digits of opcode - ram address (e.g. 0x200)
    command.nn = byte_pair & 0x00FF;  // get last two digits of opcode (in hex)
    command.n = byte_pair & 0x000F;  // get last digit of opcode (in hex)
    command.y = (byte_pair >> 4) & 0x00F;  // get third digit of opcode
    command.x = (byte_pair >> 8) & 0x0F;  // get second digit of opcode
    command.a = byte_pair >> 12;  // get first digit of opcode
    
    return command;
    
}

// Canvas and rendering

var canvas = document.getElementById('screen-canvas');
var ctx = canvas.getContext('2d');
ctx.fillStyle = '#000000';

var tile_res = 5;

var width = 64*tile_res;
var height = 32*tile_res;

canvas.setAttribute("height", height.toString());
canvas.setAttribute("width", width.toString());

// Chip8 properties and objects

var screen = create_screen(32, 64);

var ram = create_ram(4096);

var v = create_ram(16);

var stack = create_ram(16);

var sp = 0;

var pc = 512;

var i = 0;

var sound = 60;

var delay = 60;

var keys = {};

var program = [0xa2, 0x1e, 0xc2, 0x01, 0x32, 0x01, 0xa2, 0x1a, 0xd0, 0x14, 0x70, 0x04, 0x30, 0x40, 0x12, 0x00, 0x60, 0x00, 0x71, 0x04, 0x31, 0x20, 0x12, 0x00, 0x12, 0x18, 0x80, 0x40, 0x20, 0x10, 0x20, 0x40, 0x80, 0x10];

// Testing

draw_screen(screen, ctx);

for (var i = 0; i < program.length; i += 2) {

    command_to_opcode(short_to_command(shortify(program[i], program[i+1])));

}