import Phaser from 'phaser';
import { useEffect, useRef } from 'react';
import { WorldScene } from '../scenes/WorldScene';

export interface DpadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

interface PhaserGameProps {
  width: number;
  height: number;
  initTileX?: number;
  initTileY?: number;
  onSave?: (tileX: number, tileY: number) => void;
  dpadState?: DpadState;
}

export default function PhaserGame({ width, height, initTileX, initTileY, onSave, dpadState }: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<Phaser.Game | null>(null);
  // Keep onSave up-to-date without restarting Phaser on each render
  const onSaveRef = useRef(onSave);
  useEffect(() => { onSaveRef.current = onSave; }, [onSave]);

  useEffect(() => {
    if (!containerRef.current || gameRef.current) return;

    gameRef.current = new Phaser.Game({
      type: Phaser.AUTO,
      width,
      height,
      backgroundColor: '#1a1a2e',
      parent: containerRef.current,
      // No scenes in array — we start manually via postBoot to pass init data
      scene: [],
      physics: {
        default: 'arcade',
        arcade: { debug: false },
      },
      banner: false,
      callbacks: {
        postBoot: (game) => {
          game.scene.add('WorldScene', WorldScene, true, {
            tileX: initTileX ?? 20,
            tileY: initTileY ?? 20,
            onSave: (x: number, y: number) => onSaveRef.current?.(x, y),
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
