import { useDispatch } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import enhancedApi from './enhancedApi'

export const store = configureStore({
  reducer: {
    [enhancedApi.reducerPath]: enhancedApi.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(enhancedApi.middleware),
})

// Lets queries opt in to refetching when the tab regains focus.
setupListeners(store.dispatch)

type AppDispatch = typeof store.dispatch

export const useAppDispatch = () => useDispatch<AppDispatch>()
