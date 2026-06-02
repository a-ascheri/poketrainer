import Phaser from 'phaser';
import { useEffect, useRef } from 'react';
import { WorldScene } from '../scenes/WorldScene';

export interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  interact: boolean;
  blocked: boolean;
}

interface PhaserGameProps {
  width: number;
  height: number;
  initMapKey?: string;
  initTileX?: number;
  initTileY?: number;
  onSave?: (tileX: number, tileY: number, mapKey: string) => void;
  onInteract?: (message: string) => void;
  dpadState?: DpadState;
}

export default function PhaserGame({ width, height, initMapKey, initTileX, initTileY, onSave, onInteract, dpadState }: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  const onSaveRef = useRef(onSave);
  useEffect(() => { onSaveRef.current = onSave; }, [onSave]);
  const onInteractRef = useRef(onInteract);
  useEffect(() => { onInteractRef.current = onInteract; }, [onInteract]);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      width,
      height,
      backgroundColor: '#1a1a2e',
      parent: containerRef.current,
      scene: [],
      physics: {
        default: 'arcade',
        arcade: { debug: false },
      },
      banner: false,
      callbacks: {
        postBoot: (game) => {
          game.scene.add('WorldScene', WorldScene, true, {
            mapKey: initMapKey ?? 'pallet_town',
            tileX: initTileX ?? 5,
            tileY: initTileY ?? 7,
            onSave: (x: number, y: number, mk: string) => onSaveRef.current?.(x, y, mk),
            onInteract: (msg: string) => onInteractRef.current?.(msg),
            dpad: dpadState,
          });
        },
      },
    });

    return () => {
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width, height]);

  return <div ref={containerRef} style={{ lineHeight: 0 }} />;
}
