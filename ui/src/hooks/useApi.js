import { useState, useEffect } from 'react'

export const useApi = (apiFunc, params = null, immediate = true) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = async (executeParams = params) => {
    setLoading(true)
    setError(null)

    try {
      const result = await apiFunc(executeParams)
      setData(result)
      return result
    } catch (err) {
      setError(err.response?.data?.message || err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (immediate) {
      execute()
    }
  }, [])

  return { data, loading, error, execute, refetch: execute }
}

export default useApi
