import { Box, Paper } from '@mui/material';
import 'leaflet/dist/leaflet.css';
import React from 'react';
import { MapContainer, TileLayer, ZoomControl } from 'react-leaflet';

interface InteractiveMapNewProps {
  center?: [number, number];
  zoom?: number;
  children?: React.ReactNode;
}

const InteractiveMapNew: React.FC<InteractiveMapNewProps> = ({
  center = [0, 0],
  zoom = 2,
  children
}) => {
  return (
    <Paper
      elevation={2}
      sx={{
        height: '100%',
        width: '100%',
        position: 'relative',
        overflow: 'hidden',
        borderRadius: 2
      }}
    >
      <Box
        sx={{
          height: '100%',
          width: '100%',
          '& .leaflet-control-container .leaflet-top': {
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'center',
            width: '100%',
            pt: 2
          },
          '& .leaflet-control-container .leaflet-top .leaflet-control': {
            margin: '0 4px'
          },
          '& .leaflet-control-zoom': {
            border: 'none',
            borderRadius: 1,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }
        }}
      >
        <MapContainer
          center={center}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ZoomControl position="topleft" />
          {children}
        </MapContainer>
      </Box>
    </Paper>
  );
};

export default InteractiveMapNew;
