import { useDispatch } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import enhancedApi from './enhancedApi'

export const store = configureStore({
  reducer: {
    [enhancedApi.reducerPath]: enhancedApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(enhancedApi.middleware),
})

type AppDispatch = typeof store.dispatch

export const useAppDispatch = () => useDispatch<AppDispatch>()
