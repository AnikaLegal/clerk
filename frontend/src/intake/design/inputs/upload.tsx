// @flow
import React, { useRef, useState } from 'react'
import styled from 'styled-components'

import type { Upload } from 'intake/types'
import { IMAGES } from 'intake/consts'

import { theme } from '../theme'
import { ErrorMessage } from '../message'

const ALLOWED_FILE_TYPES = ['png', 'jpg', 'jpeg', 'pdf', 'docx']
const IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']

type Props = {
  values: Array<Upload>
  onChange: (any) => void
  onUpload: (File) => Promise<Upload>
  disabled: boolean
}

export const UploadInput = ({
  values,
  onChange,
  onUpload,
  disabled,
}: Props) => {
  const ref = useRef(null)
  const [isLoading, setLoading] = useState<boolean>(false)
  const [errors, setErrors] = useState<Array<string>>([])
  const onSelect = (e: React.SyntheticEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (isLoading) return
    ref.current?.click()
  }
  const onInputChange = async (e: React.SyntheticEvent<HTMLInputElement>) => {
    // @ts-ignore
    const fileList: FileList = e?.dataTransfer
      ? // @ts-ignore
        e.dataTransfer.files
      : // @ts-ignore
        e.target.files
    // There will only ever be one file at a time.
    if (!fileList || fileList.length < 1) return
    const f = fileList[0]
    // Ensure only allowed files are can be uploaded.
    const fileExtension = f.name.split('.').pop()
    const isFileTypeOk = ALLOWED_FILE_TYPES.some(
      (ext) => ext === fileExtension.toLowerCase()
    )
    const isImage = IMAGE_FILE_TYPES.includes(fileExtension)
    if (!isFileTypeOk) {
      // Reject the file, spit in the eye of our user.
      const allowedList = ALLOWED_FILE_TYPES.map((t) => `.${t}`).join(', ')
      const msg = `The file ${f.name} cannot be uploaded. Please attach only files of type ${allowedList}.`
      setErrors([msg])
    } else {
      // Accept the file, upload it.
      setLoading(true)
      try {
        const upload = await onUpload(f)
        setLoading(false)
        setErrors([])
        onChange([...values, upload])
      } catch (err) {
        setLoading(false)
        setErrors([`Could not upload ${f.name}`])
      }
    }
  }
  // Handle the user dragging the file in and out.
  const onDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }
  // Handle file drop
  const onDrop = (e) => {
    e.stopPropagation()
    e.preventDefault()
    onInputChange(e)
  }
  return (
    <>
      <HiddenInput ref={ref} type="file" onChange={onInputChange} />
      <InputContainer>
        <DropBox
          onDragEnter={onDrag}
          onDragLeave={onDrag}
          onDragOver={onDrag}
          onDrop={onDrop}
        >
          <ContentContainer>
            <TitleImg onClick={onSelect} src={IMAGES.UPLOAD} />
            <TitleEl onClick={onSelect}>
              {isLoading && <span>Uploading...</span>}
              {!isLoading && (
                <span>Upload {values.length > 0 && 'another'} file</span>
              )}
            </TitleEl>
            {values.map((f, i) => (
              <UploadedFile key={f.file} idx={i} file={f} />
            ))}
          </ContentContainer>
          <DragAndDropContainer />
        </DropBox>
      </InputContainer>
      <InputContainer>
        {errors.length > 0 &&
          errors.map((e) => <ErrorMessage key={e}>{e}</ErrorMessage>)}
      </InputContainer>
    </>
  )
}

type FileProps = {
  file: Upload
  idx: number
}

const UploadedFile = ({ file, idx }: FileProps) => {
  return (
    <UploadedFileEl>
      <a href={file.file} target="_blank">
        Uploaded file #{idx + 1}
      </a>
    </UploadedFileEl>
  )
}
const UploadedFileEl = styled.div`
  max-width: 260px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  & > a {
    text-decoration: none;
    font-size: 12px;
    color: ${theme.color.green};
    &:hover {
      color: ${theme.color.green};
    }
  }
`

const ContentContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  flex-direction: column;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
`
const DragAndDropContainer = styled.div`
  pointer-events: none;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2;
`

const TitleEl = styled.div`
  font-weight: 700;
  cursor: pointer;
  font-size: 16px;
  margin-top: 8px;
  line-height: 24px;
  color: ${theme.color.teal.secondary};
`
const TitleImg = styled.img`
  cursor: pointer;
`

const HiddenInput = styled.input`
  display: none;
`
const InputContainer = styled.div`
  max-width: 700px;
  margin: 0 auto;
`

const DropBox = styled.div`
  position: relative;
  height: 300px;
  background: ${theme.color.teal.quaternary};
  border: 2px dashed ${theme.color.teal.secondary};
  box-sizing: border-box;
  border-radius: 4px;
`
