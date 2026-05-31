import Phaser from 'phaser';

const TILE_SIZE = 16;
const SPEED = 80; // px/second

interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

interface InitData {
  tileX?: number;
  tileY?: number;
  onSave?: (tileX: number, tileY: number) => void;
  dpad?: DpadState;
}

export class WorldScene extends Phaser.Scene {
  private player!: Phaser.Types.Physics.Arcade.SpriteWithDynamicBody;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private posText!: Phaser.GameObjects.Text;
  private objectLayer!: Phaser.Tilemaps.TilemapLayer | Phaser.Tilemaps.TilemapGPULayer;
  private onSave?: (tileX: number, tileY: number) => void;
  private lastDirection: 'down' | 'up' | 'left' | 'right' = 'down';
  private _initTileX = 20;
  private _initTileY = 20;
  private dpad: DpadState = { up: false, down: false, left: false, right: false };

  constructor() {
    super({ key: 'WorldScene' });
  }

  init(data: InitData): void {
    this._initTileX = data.tileX ?? 20;
    this._initTileY = data.tileY ?? 20;
    this.onSave = data.onSave;
    if (data.dpad) this.dpad = data.dpad;
  }

  preload(): void {
    this.load.tilemapTiledJSON('pallet_town', '/maps/pallet_town.json');
    this.load.image('pokemonlike', '/tilesets/pokemonlike.png');
    // trainer.png: 64×64 spritesheet, 4 cols × 4 rows
    // Row 0 (0-3): walk-down  Row 1 (4-7): walk-up
    // Row 2 (8-11): walk-left  Row 3 (12-15): walk-right
    this.load.spritesheet('trainer', '/sprites/trainer.png', {
      frameWidth: TILE_SIZE,
      frameHeight: TILE_SIZE,
    });
  }

  create(): void {
    const map = this.make.tilemap({ key: 'pallet_town' });
    const tileset = map.addTilesetImage('pokemonlike', 'pokemonlike');

    if (!tileset) {
      console.error('[WorldScene] Failed to load tileset "pokemonlike"');
      return;
    }

    map.createLayer('ground', tileset, 0, 0);
    this.objectLayer = map.createLayer('objects', tileset, 0, 0)!;

    // All non-empty tiles in the objects layer block movement
    this.objectLayer.setCollisionByExclusion([-1]);

    const startX = this._initTileX * TILE_SIZE + TILE_SIZE / 2;
    const startY = this._initTileY * TILE_SIZE + TILE_SIZE / 2;
    this.player = this.physics.add.sprite(startX, startY, 'trainer', 0);
    this.player.setDepth(5);
    this.player.body.setSize(10, 10);

    this.physics.add.collider(this.player, this.objectLayer);

    this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1);

    this.cursors = this.input.keyboard!.createCursorKeys();
    this._createAnimations();

    this.posText = this.add
      .text(8, 8, 'Pallet Town', {
        fontSize: '9px',
        color: '#ffffff',
        backgroundColor: '#000000aa',
        padding: { x: 3, y: 2 },
      })
      .setScrollFactor(0)
      .setDepth(10);

    // Autosave every 30s
    this.time.addEvent({
      delay: 30_000,
      loop: true,
      callback: this._autosave,
      callbackScope: this,
    });
  }

  update(): void {
    if (!this.cursors || !this.player) return;

    const { left, right, up, down } = this.cursors;
    this.player.setVelocity(0, 0);

    const goLeft  = left.isDown  || this.dpad.left;
    const goRight = right.isDown || this.dpad.right;
    const goUp    = up.isDown    || this.dpad.up;
    const goDown  = down.isDown  || this.dpad.down;

    if (goLeft) {
      this.player.setVelocityX(-SPEED);
      this.lastDirection = 'left';
    } else if (goRight) {
      this.player.setVelocityX(SPEED);
      this.lastDirection = 'right';
    } else if (goUp) {
      this.player.setVelocityY(-SPEED);
      this.lastDirection = 'up';
    } else if (goDown) {
      this.player.setVelocityY(SPEED);
      this.lastDirection = 'down';
    }

    const moving = goLeft || goRight || goUp || goDown;
    if (moving) {
      this.player.play(`walk-${this.lastDirection}`, true);
    } else {
      this.player.stop();
      const idleFrame = { down: 0, up: 4, left: 8, right: 12 }[this.lastDirection];
      this.player.setFrame(idleFrame);
    }

    const tileX = Math.floor(this.player.x / TILE_SIZE);
    const tileY = Math.floor(this.player.y / TILE_SIZE);
    this.posText.setText(`Pallet Town  [${tileX}, ${tileY}]`);
  }

  private _createAnimations(): void {
    const fps = 8;
    (['down', 'up', 'left', 'right'] as const).forEach((dir, i) => {
      this.anims.create({
        key: `walk-${dir}`,
        frames: this.anims.generateFrameNumbers('trainer', { start: i * 4, end: i * 4 + 3 }),
        frameRate: fps,
        repeat: -1,
      });
    });
  }

  private _autosave(): void {
    if (!this.player || !this.onSave) return;
    const tileX = Math.floor(this.player.x / TILE_SIZE);
    const tileY = Math.floor(this.player.y / TILE_SIZE);
    this.onSave(tileX, tileY);
  }
}
