export enum Piece {
    W_PAWN = 'P',
    W_KNIGHT = 'N',
    W_BISHOP = 'B',
    W_ROOK = 'R',
    W_QUEEN = 'Q',
    W_KING = 'K',
    B_PAWN = 'p',
    B_KNIGHT = 'n',
    B_BISHOP = 'b',
    B_ROOK = 'r',
    B_QUEEN = 'q',
    B_KING = 'k',
    NONE = ''
}

export enum PlayerType {
    WHITE,
    BLACK
}

export class Square {
	private piece: Piece;
	private highlighted: Boolean;

	constructor(piece: Piece = Piece.NONE) {
		this.piece = piece;
		this.highlighted = false;
	}

	public getPiece(): Piece {
		return this.piece;
	}

	public setPiece(piece: Piece) {
		this.piece = piece;
	}

	public setHighlighted(isHighlighted: Boolean) {
		this.highlighted = isHighlighted;
	}

	public isHighlighted(): Boolean {
		return this.highlighted;
	}
}

export class Game {
	private winner: null | PlayerType;
	private turn: PlayerType;
	private moveTree: Map<String, String[]>;

	private board: Map<String, Square>;
	private currentMove: String | null;
	private key: String | null = null;

	constructor() {
		this.winner = null;
		this.turn = PlayerType.WHITE;

		this.board = new Map<String, Square>();
		this.setBoard('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR');

		this.moveTree = new Map<String, String[]>();
		this.currentMove = null;
	}

	public getBoard(): Map<String, Square> {
		return this.board;
	}

	public translatePosition(position: { x: number; y: number }): String {
		return `${String.fromCharCode(position.x + 97)}${Math.abs(position.y - 8)}`;
	}

	public getSquare(position: String): Square {
		return this.board.get(position)!;
	}

	public setSquare(position: String, piece: Piece) {
		this.board.get(position)?.setPiece(piece);
	}

	public async tryMove(position: String) {
		if (this.currentMove == null) {
			if (this.moveTree.has(position)) {
				this.currentMove = position;
			}
			else return;

			for (let move of this.moveTree.get(position)!) {
				this.getSquare(move).setHighlighted(true);
			}
		} else {
			if (this.moveTree.get(this.currentMove)?.includes(position)) {
				await this.commitMove(position);
				this.currentMove = null;
				return
			}
			this.currentMove = null;
			if (this.moveTree.has(position)) {
				this.board.forEach((v, _) => v.setHighlighted(false));
				await this.tryMove(position);
			}
		}
	}

	private async commitMove(endMove: String) {
		const response = await fetch(`http://localhost:8000/${this.key}/${this.currentMove}${endMove}`, {
			method: 'PUT'});

		if (response.status == 200) {
			await this.sync();
		}
	}

	private setBoard(fen: String) {
		let rows = fen.split('/');

		for (let y = 0; y < 8; y++) {
			let row = rows[y];
			row = row.replaceAll(/\d/g, (match) => {
				let num = parseInt(match);
				return ' '.repeat(num);
			});

			for (let x = 0; x < 8; x++) {
				let piece = row.charAt(x);
				let position = this.translatePosition({ x: x, y: y });
				if (piece == ' ') piece = Piece.NONE;

				this.board.set(position, new Square(piece as Piece));
			}
		}
	}

	public async sync() {
		const response = await fetch(`http://localhost:8000/${this.key}`);
		const data  = await response.json();

		let fen = data['fen'] as String;
		let moveTreeObject = data['moveTree'] as Record<string, string[]>;

		this.moveTree = new Map(Object.entries(moveTreeObject));
		this.setBoard(fen);

		return response.status;
	}

	public async setKey(key: String) {
		this.key = key;
		console.log("Key set to", key);
		await this.sync()
	}
}
