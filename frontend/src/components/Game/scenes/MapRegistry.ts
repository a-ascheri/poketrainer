/**
 * Central registry for all game maps.
 *
 * HOW TO ADD A NEW MAP
 * --------------------
 * 1. Create the Tiled JSON file in public/maps/<key>.json
 * 2. Add an entry to MAP_REGISTRY below.
 * 3. Add connections to/from adjacent maps.
 *
 * CONNECTION AXIS RULES
 * ----------------------
 * - top/bottom exits  → spawnY is the landing row; player X is preserved.
 * - left/right exits  → spawnX is the landing column; player Y is preserved.
 *
 * Make sure the exit tile in your map's objects layer is empty (value 0)
 * so the player can actually walk off the edge. All other border tiles
 * should be blocking (non-zero) to keep the player inside.
 *
 * FUTURE EXTENSION POINTS
 * -------------------------
 * - Add an `events` field per map for zone triggers / NPC interactions.
 * - Add a `music` field to play background music per area.
 * - Add `weather` or `lighting` flags for visual effects.
 */

export interface MapConnection {
  /** Key of the target map in MAP_REGISTRY. */
  targetMap: string;
  /**
   * Landing column (tile X) in the target map.
   * Only used for left/right exits; top/bottom exits preserve the player's current X.
   */
  spawnX: number;
  /**
   * Landing row (tile Y) in the target map.
   * Only used for top/bottom exits; left/right exits preserve the player's current Y.
   */
  spawnY: number;
}

export interface MapDef {
  key: string;
  /** Human-readable name shown on screen. */
  label: string;
  /** Phaser asset key used with load.tilemapTiledJSON. Must be unique across all maps. */
  jsonKey: string;
  /** Public URL of the Tiled JSON file (relative to /public). */
  jsonUrl: string;
  /** Phaser texture key for the shared tileset image. */
  tilesetKey: string;
  /** Public URL of the tileset image (relative to /public). */
  tilesetUrl: string;
  /** Map width in tiles (must match the Tiled JSON "width" field). */
  widthInTiles: number;
  /** Map height in tiles (must match the Tiled JSON "height" field). */
  heightInTiles: number;
  /** Name of the ground layer inside the Tiled JSON. */
  groundLayer: string;
  /** Name of the collision/objects layer inside the Tiled JSON. */
  objectLayer: string;
  /** Edge connections to neighbouring maps. Omit an edge to close it. */
  connections: {
    top?: MapConnection;
    bottom?: MapConnection;
    left?: MapConnection;
    right?: MapConnection;
  };
  /**
   * Interactive signs/noticeboards on this map.
   * When the player faces a tile at (tileX, tileY) and presses the interact button,
   * the `text` is displayed as a dialog.
   */
  signs?: Array<{ tileX: number; tileY: number; text: string }>;
}

export const MAP_REGISTRY: Record<string, MapDef> = {
  pallet_town: {
    key: 'pallet_town',
    label: 'Pallet Town',
    jsonKey: 'map_pallet_town',
    jsonUrl: '/maps/pallet_town.json',
    tilesetKey: 'pokemonlike',
    tilesetUrl: '/tilesets/pokemonlike.png',
    widthInTiles: 40,
    heightInTiles: 40,
    groundLayer: 'ground',
    objectLayer: 'objects',
    connections: {
      // Walk off the top edge → Route 1 (player X is preserved, spawns near bottom)
      top: { targetMap: 'route_1', spawnX: 0, spawnY: 57 },
    },
    signs: [
      { tileX: 25, tileY: 19, text: '¡Bienvenido a Pallet Town!' },
    ],
  },

  route_1: {
    key: 'route_1',
    label: 'Route 1',
    jsonKey: 'map_route_1',
    jsonUrl: '/maps/route_1.json',
    tilesetKey: 'pokemonlike',
    tilesetUrl: '/tilesets/pokemonlike.png',
    widthInTiles: 40,
    heightInTiles: 60,
    groundLayer: 'ground',
    objectLayer: 'objects',
    connections: {
      // Walk off the bottom edge → back to Pallet Town (player X is preserved)
      bottom: { targetMap: 'pallet_town', spawnX: 0, spawnY: 2 },
    },
  },
};

export const DEFAULT_MAP = 'pallet_town';
