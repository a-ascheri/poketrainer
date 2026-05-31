import Phaser from 'phaser';
import { MAP_REGISTRY, DEFAULT_MAP, type MapDef } from './MapRegistry';

const TILE_SIZE = 16;
const SPEED = 80; // px/second
/** How many pixels past the map edge before a transition fires. */
const TRANSITION_PX = TILE_SIZE;

interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

interface InitData {
  mapKey?: string;
  tileX?: number;
  tileY?: number;
  onSave?: (tileX: number, tileY: number, mapKey: string) => void;
  dpad?: DpadState;
}

export class WorldScene extends Phaser.Scene {
  private player!: Phaser.Types.Physics.Arcade.SpriteWithDynamicBody;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private posText!: Phaser.GameObjects.Text;
  private objectLayer!: Phaser.Tilemaps.TilemapLayer | Phaser.Tilemaps.TilemapGPULayer;
  private onSave?: (tileX: number, tileY: number, mapKey: string) => void;
  private lastDirection: 'down' | 'up' | 'left' | 'right' = 'down';
  private _initTileX = 5;
  private _initTileY = 7;
  private _transitioning = false;
  private currentMapDef!: MapDef;
  private mapWidthPx = 0;
  private mapHeightPx = 0;
  private dpad: DpadState = { up: false, down: false, left: false, right: false };

  constructor() {
    super({ key: 'WorldScene' });
  }

  init(data: InitData): void {
    const mapKey = data.mapKey ?? DEFAULT_MAP;
    this.currentMapDef = MAP_REGISTRY[mapKey] ?? MAP_REGISTRY[DEFAULT_MAP];
    this._initTileX = data.tileX ?? 5;
    this._initTileY = data.tileY ?? 7;
    this.onSave = data.onSave;
    this._transitioning = false;
    if (data.dpad) this.dpad = data.dpad;
  }

  preload(): void {
    const def = this.currentMapDef;
    // Phaser's loader skips assets that are already in the cache.
    this.load.tilemapTiledJSON(def.jsonKey, def.jsonUrl);
    this.load.image(def.tilesetKey, def.tilesetUrl);
    // trainer.png: 64×64 spritesheet, 4 cols × 4 rows
    // Row 0 (0-3): walk-down  Row 1 (4-7): walk-up
    // Row 2 (8-11): walk-left  Row 3 (12-15): walk-right
    this.load.spritesheet('trainer', '/sprites/trainer.png', {
      frameWidth: TILE_SIZE,
      frameHeight: TILE_SIZE,
    });
  }

  create(): void {
    const def = this.currentMapDef;
    const map = this.make.tilemap({ key: def.jsonKey });
    const tileset = map.addTilesetImage(def.tilesetKey, def.tilesetKey);

    if (!tileset) {
      console.error(`[WorldScene] Failed to load tileset "${def.tilesetKey}"`);
      return;
    }

    map.createLayer(def.groundLayer, tileset, 0, 0);
    this.objectLayer = map.createLayer(def.objectLayer, tileset, 0, 0)!;
    // All non-empty tiles in the objects layer block movement
    this.objectLayer.setCollisionByExclusion([-1]);

    this.mapWidthPx  = map.widthInPixels;
    this.mapHeightPx = map.heightInPixels;

    const startX = this._initTileX * TILE_SIZE + TILE_SIZE / 2;
    const startY = this._initTileY * TILE_SIZE + TILE_SIZE / 2;
    this.player = this.physics.add.sprite(startX, startY, 'trainer', 0);
    this.player.setDepth(5);
    this.player.body.setSize(10, 10);

    this.physics.add.collider(this.player, this.objectLayer);

    this.cameras.main.setBounds(0, 0, this.mapWidthPx, this.mapHeightPx);
    this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
    this.cameras.main.fadeIn(300, 0, 0, 0);

    this.cursors = this.input.keyboard!.createCursorKeys();
    this._createAnimations();

    this.posText = this.add
      .text(8, 8, def.label, {
        fontSize: '9px',
        color: '#ffffff',
        backgroundColor: '#000000aa',
        padding: { x: 3, y: 2 },
      })
      .setScrollFactor(0)
      .setDepth(10);

    // Autosave every 30 s
    this.time.addEvent({
      delay: 30_000,
      loop: true,
      callback: this._autosave,
      callbackScope: this,
    });
  }

  update(): void {
    if (!this.cursors || !this.player || this._transitioning) return;

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
    this.posText.setText(`${this.currentMapDef.label}  [${tileX}, ${tileY}]`);

    this._checkTransitions(tileX, tileY);
  }

  // ─── Map transitions ───────────────────────────────────────────────────────

  /**
   * Detects when the player walks off any open edge and fires the transition.
   * The "carried" axis (X for vertical exits, Y for horizontal exits) is taken
   * from the player's current tile so the entry point feels natural.
   */
  private _checkTransitions(tileX: number, tileY: number): void {
    const { connections } = this.currentMapDef;
    const px = this.player.x;
    const py = this.player.y;

    if (connections.top && py < -TRANSITION_PX) {
      this._transitionTo(connections.top.targetMap, tileX, connections.top.spawnY);
    } else if (connections.bottom && py > this.mapHeightPx + TRANSITION_PX) {
      this._transitionTo(connections.bottom.targetMap, tileX, connections.bottom.spawnY);
    } else if (connections.left && px < -TRANSITION_PX) {
      this._transitionTo(connections.left.targetMap, connections.left.spawnX, tileY);
    } else if (connections.right && px > this.mapWidthPx + TRANSITION_PX) {
      this._transitionTo(connections.right.targetMap, connections.right.spawnX, tileY);
    }
  }

  /**
   * Fades out and restarts the scene with the target map.
   * Calls onSave immediately so the backend reflects the new location
   * before the scene restarts.
   */
  private _transitionTo(targetMapKey: string, spawnX: number, spawnY: number): void {
    if (this._transitioning) return;
    this._transitioning = true;

    // Persist new position to the backend immediately
    this.onSave?.(spawnX, spawnY, targetMapKey);

    this.cameras.main.fadeOut(250, 0, 0, 0);
    this.cameras.main.once(
      Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE,
      () => {
        this.scene.restart({
          mapKey: targetMapKey,
          tileX: spawnX,
          tileY: spawnY,
          onSave: this.onSave,
          dpad: this.dpad,
        } satisfies InitData);
      },
    );
  }

  // ─── Helpers ──────────────────────────────────────────────────────────────

  private _createAnimations(): void {
    const fps = 8;
    (['down', 'up', 'left', 'right'] as const).forEach((dir, i) => {
      // Animation keys are global to the Phaser.Game; guard against duplicates
      // that occur when the scene is restarted during a map transition.
      if (!this.anims.exists(`walk-${dir}`)) {
        this.anims.create({
          key: `walk-${dir}`,
          frames: this.anims.generateFrameNumbers('trainer', { start: i * 4, end: i * 4 + 3 }),
          frameRate: fps,
          repeat: -1,
        });
      }
    });
  }

  private _autosave(): void {
    if (!this.player || !this.onSave) return;
    const tileX = Math.floor(this.player.x / TILE_SIZE);
    const tileY = Math.floor(this.player.y / TILE_SIZE);
    this.onSave(tileX, tileY, this.currentMapDef.key);
  }
}
