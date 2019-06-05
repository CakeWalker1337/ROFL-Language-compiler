

define i8* @func.f(i8* %str, i32 %a) {
    %str.ptr = alloca i8*
    %a.ptr = alloca i32
    store i8* %str, i8** %str.ptr
    store i32 %a, i32* %a.ptr
    %str.1 = load i8*, i8** %str.ptr
    ret i8* %str.1
}

define i32 @main() {
    %str.ptr = alloca i8*
    store i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.1, i32 0, i32 0), i8** %str.ptr
    %s.ptr = alloca i8*
    %f.2 = call i8* @func.f(i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str.2, i32 0, i32 0), i32 2)
    store i8* %f.2, i8** %s.ptr
    %s.3 = load i8*, i8** %s.ptr
    %buffer5 = getelementptr inbounds [5 x i8], [5 x i8]* @.str.3, i32 0, i32 0 
    call i32 (i8*, ...) @printf(i8* %buffer5, i8* %s.3)
    ret i32 0
}

declare i32 @printf(i8*, ...)
@.str.1 = private unnamed_addr constant [4 x i8] c"123\00", align 1
@.str.2 = private unnamed_addr constant [6 x i8] c"12312\00", align 1
@.str.3 = private unnamed_addr constant [5 x i8] c"%s4\0A\00", align 1
