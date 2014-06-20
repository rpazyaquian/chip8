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
    
    for (var i = 0; i<screen_height; i++) {
        screen[i] = new Array(64);
        for (var j = 0; j<screen_width; j++) {
            screen[i][j] = 0;
        }
    }
    
    return screen;
}

function bit_to_pixel(input_byte) {

    pixel_array = [];

    for (var i = 0; i<8; i++) {
        p = ((input_byte >> i) & 1);
        pixel_array[7-i] = p;
    }

    return pixel_array;
}

function create_sprite_array(height) {
    sprite_array = [];

    for (var i = 0; i < height; i++) {
        sprite_array[i] = bit_to_pixel(ram[index+i]);
    }

    return sprite_array;
}

function draw_sprite(array, x_off, y_off) {

    v[15] = 0;  // vf checks for collision. if collision, vf = 1.

    for (var i = 0; i < array.length; i++) {  // for every row (each row contains an array) in sprite array...
        for (var j = 0; j < 8; j++) {  // for every element in each row array (i.e. each pixel)...
            if (i + y_off <= 31 && j + x_off <= 63) {  // if the coordinate to draw to is within a 64x32 bound...
                if (screen[i+y_off][j+x_off] == 1) {  // if the pixel located at the corresponding coordinate in the screen is 1...
                    if ((screen[i+y_off][j+x_off] ^ array[i][j]) === 0) {  // if the pixel to be drawn over and the corresponding sprite pixel are both 1...
                        v[15] = 1;  // set vf to 1, because a collision has occurred.
                    }
                }

                screen[i+y_off][j+x_off] = (screen[i+y_off][j+x_off] ^ array[i][j]);  // set the pixel to be drawn equal to the xor of both pixels.
                // i.e., the sprite "flips" the screen section for all sprite pixels = 1.
            }
        }
    }

}

// Rendering functions

function draw_screen(screen, context) {
    
    // this is drawing the screen to the canvas! not to the array! remember this!

    // clear the canvas for redraw

    context.clearRect(0, 0, canvas.width, canvas.height)

    for (var i = 0; i < screen.length; i++) {

        for (var j = 0; j < screen[i].length; j++) {

            var value = screen[i][j];
            
            if (value === 0) {
                context.fillStyle = off_color;
                context.fillRect(j*tile_res, i*tile_res, tile_res, tile_res);
            } else {
                context.fillStyle = on_color;
                context.fillRect(j*tile_res, i*tile_res, tile_res, tile_res);
            }
        }

    }

}

// Logic functions

function clear_screen() {
    
    // console.log('clear screen');

    for (var i = 0; i < screen.length; i++) {
        for (var j = 0; j < screen[i].length; j++) {
            screen[i][j] = 0;
        }
    }

}

function return_from_stack() {
    
    // console.log('return from stack');

    sp -= 1;
    pc = stack[sp];

}

function jump(nnn) {
    
    // console.log('jump to address');

    // if the address being jumped to is equal to the program counter minus 2, i.e. there is a loop occurring, stop the entire program.

    if (pc === (nnn + 2)) {
        end_loop = true;
        pc = nnn;
    } else {
        pc = nnn;
    }

}

function call_stack(nnn) {
    
    // console.log('call stack');

    // console.log(stack);
    // console.log(sp);
    // console.log(pc);
    // console.log(nnn);

    stack[sp] = pc;
    sp++;
    pc = nnn;

    // console.log(stack);
    // console.log(sp);
    // console.log(pc);

}

function skip_if_vx_equal_nn(x, nn) {
    
    // console.log('skip if vx == nn');

    if (v[x] === nn) {
        pc += 2;
    }

}

function skip_if_vx_not_equal_nn(x, nn) {
    
    // console.log('skip if vx != nn');
    
    if (v[x] !== nn) {
        pc += 2;
    }
}

function skip_if_vx_equal_vy(x, y) {
    
    // console.log('skip if vx == vy');
    
    if (v[x] === v[y]) {
        pc += 2;
    }
}

function set_vx_to_nn(x, nn) {
    
    // console.log('set v'+x+' to '+nn);
    
    v[x] = nn;
}

function add_nn_to_vx(x, nn){
    
    // console.log('add '+nn+' to v'+x);
    
    v[x] += nn;
    if (v[x] > 0xFF) {
        v[x] -= 0xFF;
    }
}

function set_vx_to_vy(x, y) {
    
    // console.log('set vx to vy');
    
    v[x] = v[y];
}

function set_vx_to_vx_or_vy(x, y) {
    
    // console.log('set vx to (vx || vy)');
    
    v[x] = (v[x] | v[y]);
}

function set_vx_to_vx_and_vy(x, y) {
    
    // console.log('set vx to (vx && vy)');
    
    v[x] = (v[x] & v[y]);
}

function set_vx_to_vx_xor_vy(x, y) {
    
    // console.log('set vx to (vx ^ vy)');
    
    v[x] = (v[x] ^ v[y]);
}

function add_vy_to_vx(x, y) {
        
    // console.log('add vy to vx');
    
    // vf is set to 1 when there is a carry (vx + vy > 255), set to 0 when there isn't
    if ((v[x] + v[y]) > 0xFF) {
        v[15] = 1;
        v[x] += v[y];
        v[x] -= 0xFF;
    } else {
        v[15] = 0;
        v[x] += v[y];
    }
}

function subtract_vy_from_vx(x, y) {
    
    // console.log('subtract vy from vx');
    
    // vf is set to 0 when there's a borrow (vx - vy < 0), set to 1 when there isn't
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

function shift_vx_right(x) {
    
    // console.log('shift vx right by 1');
    
    // vf is set to the value of the least significant ('rightmost') bit before the shift
    v[15] = (v[x] & 1);
    v[x] = (v[x] >> 1);
}

function set_vx_to_vy_minus_vx(x, y) {
    
    // console.log('set vx to (vy minus vx)');
    
    // vf is set to 0 when there's a borrow, set to 1 when there isn't
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

function shift_vx_left(x) {
    
    // console.log('shift vx left by 1');
    
    // vf is set to the value of the most significant ('leftmost') bit before the shift
    v[15] = (v[x] & 0x80) >> 7;  // e.g. (0x7F & 0x80) --> (0111 1111 & 1000 0000), >> 7 = 0. basically, vf = 0 if vx < 128, else vf = 1.  (this works, iirc)
    v[x] = (v[x] << 1); // e.g. 0x7F = 01111111 << 1

    if (v[x] > 255) {
        v[x] -= 256;
    }

    // in javascript, 0xFF = 11111111 << 1 is set to 111111110 (510), instead of 11111110 (254 = 0xFE). Figure out a solution!
    // 0xFF == 1111 1111 = 255
    // << --> 1 1111 1110 = 510
    // actual result should be 1111 1110 = 254
    // 510 - 256 = 254
    // so if the result is larger than 255, subtract by 256
    // 1000 000 = 128
    // << --> 1 0000 0000 = 256
    // actual result should be 0000 0000 = 0.
    // so yeah, if larger than 255, minus by 256.
    // 256 -> 0, 257 (1 0000 0001) -> 1 (0000 0001), 458 (1 1100 1010) --> 202 (1100 1010).
}

function skip_if_vx_not_equal_vy(x, y) {
    
    // console.log('skip next instruction if vx is not equal to vy');
    
    if (v[x] != v[y]) {
        pc += 2;
    }
}

function set_index_to_nnn(nnn) {
    
    // console.log('set index to nnn (nnn is already translated to decimal)');
    
    index = nnn;
}

function jump_to_nnn_plus_v0(nnn) {
    
    // console.log('jump to (nnn + v0)');
    
    pc = (nnn + v[0]);
}

function set_vx_to_random_number_and_nn(x, nn) {
    
    // console.log('set vx to (random number && nn)');
    
    v[x] = (randrange(0, 255) & nn);
}

function draw_n_large_sprite_at_vx_vy(x, y, n) {

    // console.log('draw n large sprite at (vx, vy)');
    
    s_array = create_sprite_array(n);
    draw_sprite(s_array, v[x], v[y]); // oh god i'm an idiot
}

function skip_if_key_with_value_vx_is_pressed(x) {

    // console.log('skip if key with value vx is pressed');

    key_on_off = keys[key_translations[v[x]]];  // v[x] = 0, key_trans[0] = 48, keys[48] = true or false

    if (key_on_off) {
        pc += 2;
    }
}

function skip_if_key_with_value_vx_is_not_pressed(x) {

    // console.log('skip if key with value vx is not pressed');

    key_on_off = keys[key_translations[v[x]]];  // v[x] = 0, key_trans[0] = 48, keys[48] = true or false

    if (!key_on_off) {
        pc += 2;
    }
}

function set_vx_to_value_of_delay_timer(x) {
    
    // console.log('set vx to value of delay timer');
    
    v[x] = delay;
}

function await_key_and_store_in_vx(x) {

    pc -= 2;  // decrement the pc by two so the paused opcodes will begin here again

    // console.log(waiting_for_key);

    // if we are not waiting for a key and captured_key < 0:
        // 
    // else if we are not waiting for a key and captured key >= 0 (i.e. was assigned a value by jquery):
        //
    // else we are waiting for a key anddddd wait, no.
        // as it is right now, there is no way that waiting_for_key can be true when coming into this opcode
        // if waiting_for_key is true before we run an opcode, then...doesn't it break out of the for loop?
    // so the question is, is captured_key < 0 (i.e. did we just assign it or has it been reset)?

    if (!waiting_for_key && captured_key < 0) {
        waiting_for_key = true;
    } else {
        v[x] = captured_key;
        waiting_for_key = false;
        captured_key = -1;  // reset captured key for the next time this opcode occurs
        pc += 2;
    }
    
}

function set_delay_to_vx(x) {
    
    // console.log('set delay timer to vx');
    
    delay = v[x];
}

function set_sound_to_vx(x) {
    
    // console.log('set sound timer to vx');
    
    sound = v[x];
}

function add_vx_to_index(x) {
    
    // console.log('add vx to index');
    
    index = (index + v[x]);
}

function set_index_to_location_of_sprite_for_vx(x) {

    // console.log('set index to location of sprite for digit '+x);
    index = v[x] * 5;
}

function store_binary_coded_rep_of_vx(x) {

    // console.log('store binary coded rep of vx');

    ones = v[x] % 10;
    tens = Math.floor(v[x] / 10) % 10; // 254 / 10 --> 25, 25 % 10 --> 5
    hundreds = Math.floor(v[x] / 100) % 10;  // 254 / 100 --> 2, 2 % 10 --> 2
    
    ram[index] = hundreds;
    ram[index+1] = tens;
    ram[index+2] = ones;
}

function store_v0_to_vx_in_memory_starting_at_index(x) {

    // console.log('store v0 to vx in memory starting at index');

    for (var i = 0; i < x+1; i++) {
        ram[index+i] = v[i];
    }
}

function fill_v0_to_vx_from_memory_starting_at_index(x) {

    // console.log('fill v0 to vx from memory starting at index');

    for (var i = 0; i < x+1; i++) {
        v[i] = ram[index+i];
    }
}

function command_to_opcode(command) {

    pc += 2;
   
    switch(command.a) {
    
        case 0:
            
            switch(command.insn) {
            
                case 224:
                    clear_screen();
                    break;
                    
                case 238:
                    return_from_stack();
                    break;
                    
                default:
                    // console.log("invalid opcode");
                    break;
            
            }
            
            break;
        
        case 1:
            
            jump(command.nnn);
            
            break;
        
        case 2:
            
            call_stack(command.nnn);
            
            break;
        
        case 3:
            
            skip_if_vx_equal_nn(command.x, command.nn);
            
            break;
        
        case 4:
            
            skip_if_vx_not_equal_nn(command.x, command.nn);
            
            break;
        
        case 5:
            
            skip_if_vx_equal_vy(command.x, command.y);
            
            break;
        
        case 6:
            
            set_vx_to_nn(command.x, command.nn);
            
            break;
        
        case 7:
            
            add_nn_to_vx(command.x, command.nn);
            
            break;
        
        case 8:
            
            switch(command.n) {
            
                case 0:
                    
                    set_vx_to_vy(command.x, command.y);
                    
                    break;
                case 1:
                    
                    set_vx_to_vx_or_vy(command.x, command.y);
                    
                    break;
                case 2:
                    
                    set_vx_to_vx_and_vy(command.x, command.y);
                    
                    break;
                case 3:
                    
                    set_vx_to_vx_xor_vy(command.x, command.y);
                    
                    break;
                case 4:
                    
                    add_vy_to_vx(command.x, command.y);
                    
                    break;
                case 5:
                    
                    subtract_vy_from_vx(command.x, command.y);
                    
                    break;
                case 6:
                    
                    // shift right 1
                    shift_vx_right(command.x);
                    
                    break;
                case 7:
                    
                    // set vx to (vx - vy)
                    set_vx_to_vy_minus_vx(command.x, command.y);
                    
                    break;
                case 14:
                    
                    // shift left 1
                    shift_vx_left(command.x);
                    
                    break;
            
            }
            
            break;
        
        case 9:
            
            skip_if_vx_not_equal_vy(command.x, command.y);
            
            break;
        
        case 10:
            
            set_index_to_nnn(command.nnn);
            
            break;
        
        case 11:
            
            // jump to NNN + V0
            jump_to_nnn_plus_v0(command.nnn);
            
            break;
        
        case 12:
            
            // set VX to (random number & NN)
            set_vx_to_random_number_and_nn(command.x, command.nn);
            
            break;
        
        case 13:
            // "Sprites stored in memory at location in index register (I), maximum 8bits wide. Wraps around the screen.
            // If when drawn, clears a pixel, register VF is set to 1 otherwise it is zero. All drawing is XOR drawing (e.g. it toggles the screen pixels)"
            draw_n_large_sprite_at_vx_vy(command.x, command.y, command.n);
            
            break;
        
        case 14:
            
            switch(command.nn) {
            
                case 158:
                    
                    skip_if_key_with_value_vx_is_pressed(command.x);
                    
                    break;
                case 161:
                    
                    skip_if_key_with_value_vx_is_not_pressed(command.x);
                    
                    break;
                default:
                    // console.log('invalid opcode');
                    break;
            
            }
            
            break;
        
        case 15:
            
            switch(command.nn) {

                case 7:

                    set_vx_to_value_of_delay_timer(command.x);
                    break;

                case 10:

                    await_key_and_store_in_vx(command.x);
                    break;

                case 21:

                    set_delay_to_vx(command.x);
                    break;

                case 24:

                    set_sound_to_vx(command.x);
                    break;

                case 30:

                    // set index to (index + vx)
                    add_vx_to_index(command.x);

                    break;

                case 41:

                    // set index to location of sprite for character X. (e.g. 0, 1, E, F)
                    set_index_to_location_of_sprite_for_vx(command.x);

                    break;

                case 51:

                    // store binary-coded decimal rep of VX, hundreds digit @ I, tens digit @ I+1, ones digit @ I+2
                    store_binary_coded_rep_of_vx(command.x); 

                    break;

                case 85:

                    // store v0 to vx in memory starting at I
                    store_v0_to_vx_in_memory_starting_at_index(command.x);

                    break;

                case 101:

                    // fill v0 to vx with values from memory starting at I
                    fill_v0_to_vx_from_memory_starting_at_index(command.x);

                    break;

            }
            
            break;
        
        default:
            // console.log('invalid opcode');
    
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

var tile_res = 20;

var width = 64*tile_res;
var height = 32*tile_res;

canvas.setAttribute("height", height.toString());
canvas.setAttribute("width", width.toString());

// Chip8 properties and objects

program = [0xa2, 0x1e, 0xc2, 0x01, 0x32, 0x01, 0xa2, 0x1a, 0xd0, 0x14, 0x70, 0x04, 0x30, 0x40, 0x12, 0x00, 0x60, 0x00, 0x71, 0x04, 0x31, 0x20, 0x12, 0x00, 0x12, 0x18, 0x80, 0x40, 0x20, 0x10, 0x20, 0x40, 0x80, 0x10];

off_color = "#000000";
on_color = "#FFFFFF";

key_translations = {
    0: 88, // 0
    1: 49, // 1
    2: 50, // 2
    3: 51, // 3
    4: 81, // 4
    5: 87, // 5
    6: 69, // 6
    7: 65, // 7
    8: 83, // 8
    9: 68, // 9
    10: 90, // a
    11: 67, // b
    12: 52, // c
    13: 82, // d
    14: 70, // e
    15: 86 // f
};

key_reverse = {
    88: 0, // 0
    49: 1, // 1
    50: 2, // 2
    51: 3, // 3
    81: 4, // 4
    87: 5, // 5
    69: 6, // 6
    65: 7, // 7
    83: 8, // 8
    68: 9, // 9
    90: 10, // a
    67: 11, // b
    52: 12, // c
    82: 13, // d
    70: 14, // e
    86: 15 // f
};

function load_program() {
    for (var i = 0; i < program.length; i++) {

        ram[512 + i] = program[i];

    }
}

function load_font() {

    // 0x000 through (5 * 16 = 80) 0x50(?)/0x4F(?), anyway the first 80 bytes in ram are font data.

    font_data = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,
        0x20, 0x60, 0x20, 0x20, 0x70,
        0xF0, 0x10, 0xF0, 0x80, 0xF0,
        0xF0, 0x10, 0xF0, 0x10, 0xF0,
        0x90, 0x90, 0xF0, 0x10, 0x10,
        0xF0, 0x80, 0xF0, 0x10, 0xF0,
        0xF0, 0x80, 0xF0, 0x90, 0xF0,
        0xF0, 0x10, 0x20, 0x40, 0x40,
        0xF0, 0x90, 0xF0, 0x90, 0xF0,
        0xF0, 0x90, 0xF0, 0x10, 0xF0,
        0xF0, 0x90, 0xF0, 0x90, 0x90,
        0xE0, 0x90, 0xE0, 0x90, 0xE0,
        0xF0, 0x80, 0x80, 0x80, 0xF0,
        0xE0, 0x90, 0x90, 0x90, 0xE0,
        0xF0, 0x80, 0xF0, 0x80, 0xF0,
        0xF0, 0x80, 0xF0, 0x80, 0x80
    ];

    for (var i = 0; i<font_data.length; i++) {
        ram[i] = font_data[i];
    }
}

// Main program functions

function initialize_chip8() {
    screen = create_screen(32, 64);

    ram = create_ram(4096);

    v = create_ram(16);

    stack = create_ram(16);

    sp = 0;

    pc = 512;

    index = 0;

    sound = 60;

    delay = 60;

    keys = {
        88: false, // 0
        49: false, // 1
        50: false, // 2
        51: false, // 3
        81: false, // 4
        87: false, // 5
        69: false, // 6
        65: false, // 7
        83: false, // 8
        68: false, // 9
        90: false, // a
        67: false, // b
        52: false, // c
        82: false, // d
        70: false, // e
        86: false // f
    };

    waiting_for_key = false;

    captured_key = -1;

    load_font();

    load_program();

    draw_screen(screen, ctx);

}

function frame_loop() {

    // this is run every 1/60th of a second

    // console.log('running loop');

    if (!waiting_for_key) {
        for (var i = 0; i < 10; i++) {  // run ten opcodes   
            run_opcode();
            if (waiting_for_key) break;
        }
    }

    // don't forget to count down the timers!

    if (sound > 0) {
        sound -= 1;
    }

    if (delay > 0) {
        delay -= 1;
    }

    draw_screen(screen, ctx);

}

function run_opcode() {

    command_to_opcode(short_to_command(shortify(ram[pc], ram[pc+1])));

}

function set_run_status(bool) {
    if(bool) {
        initialize_chip8();
        timer = setInterval(function() {
            frame_loop();
        }, 1000/60);
    } else {
        clearInterval(timer);
    }
}