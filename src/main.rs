use rand::seq::SliceRandom;
use rand::{thread_rng, Rng};
use std::io;
use std::io::Read;

use termion::raw::IntoRawMode;
use std::borrow::Cow;
const SIZE: usize = 4;

#[derive(Clone)]
struct GameBoard {
    cells: [[Option<u32>; SIZE]; SIZE],
    score: u32,
}

fn initialize_board() -> GameBoard {
    let mut board = GameBoard {
        cells: [[None; SIZE]; SIZE],
        score: 0,
    };
    add_random_tile(&mut board);
    add_random_tile(&mut board);
    board
}

fn slide_left(mut row: [Option<u32>; SIZE], score: &mut u32) -> [Option<u32>; SIZE] {
    let mut new_row = [None; SIZE];
    let mut idx = 0;

    for &cell in row.iter() {
        if cell.is_some() {
            new_row[idx] = cell;
            idx += 1;
        }
    }

    idx = 0;
    while idx < SIZE - 1 {
        if new_row[idx] == new_row[idx + 1] && new_row[idx].is_some() {
            new_row[idx] = new_row[idx].map(|x| x * 2);
            new_row[idx + 1] = None;
            *score += new_row[idx].unwrap();
            idx += 2;
        } else {
            idx += 1;
        }
    }

    let mut final_row = [None; SIZE];
    idx = 0;
    for &cell in new_row.iter() {
        if cell.is_some() {
            final_row[idx] = cell;
            idx += 1;
        }
    }
    final_row
}

fn slide_right(mut row: [Option<u32>; SIZE], score: &mut u32) -> [Option<u32>; SIZE] {
    row.reverse();
    let new_row = slide_left(row, score);
    new_row.iter().rev().cloned().collect::<Vec<_>>().try_into().unwrap()
}

fn slide_up(mut col: [Option<u32>; SIZE], score: &mut u32) -> [Option<u32>; SIZE] {
    slide_left(col, score)
}

fn slide_down(mut col: [Option<u32>; SIZE], score: &mut u32) -> [Option<u32>; SIZE] {
    col.reverse();
    let new_col = slide_left(col, score);
    new_col.iter().rev().cloned().collect::<Vec<_>>().try_into().unwrap()
}

fn make_move(board: &mut GameBoard, direction: MoveDirection) {
    match direction {
        MoveDirection::Left => {
            for i in 0..SIZE {
                board.cells[i] = slide_left(board.cells[i], &mut board.score);
            }
        }
        MoveDirection::Right => {
            for i in 0..SIZE {
                board.cells[i] = slide_right(board.cells[i], &mut board.score);
            }
        }
        MoveDirection::Up => {
            for i in 0..SIZE {
                let mut col = [
                    board.cells[0][i],
                    board.cells[1][i],
                    board.cells[2][i],
                    board.cells[3][i],
                ];
                col = slide_up(col, &mut board.score);
                for j in 0..SIZE {
                    board.cells[j][i] = col[j];
                }
            }
        }
        MoveDirection::Down => {
            for i in 0..SIZE {
                let mut col = [
                    board.cells[0][i],
                    board.cells[1][i],
                    board.cells[2][i],
                    board.cells[3][i],
                ];
                col = slide_down(col, &mut board.score);
                for j in 0..SIZE {
                    board.cells[j][i] = col[j];
                }
            }
        }
    }
}

fn add_random_tile(board: &mut GameBoard) {
    let mut rng = thread_rng();
    let mut empty_cells = Vec::new();
    for i in 0..SIZE {
        for j in 0..SIZE {
            if board.cells[i][j].is_none() {
                empty_cells.push((i, j));
            }
        }
    }
    if let Some(&(x, y)) = empty_cells.choose(&mut rng) {
        board.cells[x][y] = Some(if rng.gen_bool(0.9) { 2 } else { 4 });
    }
}

fn is_game_over(board: &GameBoard) -> bool {
    for i in 0..SIZE {
        for j in 0..SIZE {
            if board.cells[i][j].is_none() {
                return false;
            }
            if j < SIZE - 1 && board.cells[i][j] == board.cells[i][j + 1] {
                return false;
            }
            if i < SIZE - 1 && board.cells[i][j] == board.cells[i + 1][j] {
                return false;
            }
        }
    }
    true
}

fn boards_are_identical(board1: &GameBoard, board2: &GameBoard) -> bool {
    for i in 0..SIZE {
        for j in 0..SIZE {
            if board1.cells[i][j] != board2.cells[i][j] {
                return false;
            }
        }
    }
    true
}

enum MoveDirection {
    Up,
    Down,
    Right,
    Left,
}

fn main() {
    print!("{}", termion::clear::All);
    
    let mut board = initialize_board();

    // let is_tty = atty::is(atty::Stream::Stdin);

    // // Required to get the terminal to respond to I/O directly.
    // if is_tty {
    //     let _stdout = io::stdout().into_raw_mode().unwrap();
    // }

    let mut bytes_iter: Box<dyn Iterator<Item = io::Result<u8>>>;

    
    bytes_iter = Box::new(io::stdin().bytes());
    

    let mut row = 1; // Starting row position
    let mut col = 1; // Starting column position
    
    let mut last_move_valid = true;
    let mut moves = 0;
    loop {

        // Clear the screen
        

        // Print the board by looping over elements
      

        // Reset the row and column positions for the next iteration
        row = 1;
        col = 1;

        // Print the score
        
        //println!("Score: {}", SCORE);

        // Move to the next row for the "Enter a move" prompt
        row += 1;


        row += 1;
        // Initialize the previous board to detect any changes after a move
        let previous_board = board.clone();

        // Print the "Enter a move" prompt justified to the left
        print!("{}", termion::clear::All);
        print!("{}", termion::cursor::Goto(1, row));

        for board_row in board.cells.iter() {
            for cell in board_row.iter() {
                let cell_str: Cow<str> =
                    cell.map_or(Cow::Borrowed("."), |n| Cow::Owned(n.to_string()));

                // Move cursor to the current position and print the cell
                print!("{}", termion::cursor::Goto(col, row));
                print!("{:<5}", cell_str);

                col += 7; // Move the column position for the next cell
            }
            col = 1; // Reset the column position for the next row
            row += 1; // Move to the next row
        }
        print!("{}", termion::cursor::Goto(1, row));
        print!("Score: {}  Moves: {} ", board.score, moves);
        if is_game_over(&board) {
            println!("X");
        } else if last_move_valid {
            println!("~");
        } else {
            println!("!");
        }
        if let Some(input) = bytes_iter.next() {
            let move_made = match input {
                
                Ok(byte) => {
                    
                    match byte {
                        b'u' => {
                            make_move(&mut board, MoveDirection::Up);
                            moves += 1;
                            true
                        }
                        b'd' => {
                            make_move(&mut board, MoveDirection::Down);
                            moves += 1;
                            true
                        }
                        b'r' => {
                            make_move(&mut board, MoveDirection::Right);
                            moves += 1;
                            true
                        }
                        b'l' => {
                            make_move(&mut board, MoveDirection::Left);
                            moves += 1;
                            true
                        }
                        b'f' => {
                            // refresh output
                            true
                        }
                        b'q' => {
                            println!("Quitting the game.");
                            return; // Exit the program
                        }
                        3 => {
                            // CTRL+C
                            println!("Quitting the game.");
                            return; // Exit the program
                        }
                        _ => false,
                    }
                }
                _ => false,
            };
            
            // Inside your main loop, after making a move
            if move_made {
                // Only add a new tile if the board changed
                if !boards_are_identical(&board, &previous_board) {
                    add_random_tile(&mut board);
                    last_move_valid = true;
                } else {
                    last_move_valid = false;
                }
            } else {
                std::thread::sleep(std::time::Duration::from_millis(1)); // Brief pause to prevent CPU overuse
            }
        } else {
            std::thread::sleep(std::time::Duration::from_millis(1)); // Brief pause to prevent CPU overuse
        }
    }
}